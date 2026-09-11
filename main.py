from flask import Flask, render_template, request, jsonify, send_file
import logging
from pathlib import Path
from config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, LOG_LEVEL, LOG_FILE, 
    UPLOAD_DIR, TEMP_DIR, DEFAULT_FINAL_DURATION, CLIP_DURATION
)
from groq_handler import groq
from youtube_handler import youtube
from video_processor import processor
from voice_handler import voice
from db import db
import os
import json

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1500 * 1024 * 1024  # 1.5GB max

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Check if all dependencies are available"""
    try:
        import subprocess
        # Check FFmpeg
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        ffmpeg_ok = True
    except:
        ffmpeg_ok = False
    
    try:
        import subprocess
        # Check yt-dlp
        subprocess.run(['yt-dlp', '--version'], capture_output=True, timeout=5)
        ytdlp_ok = True
    except:
        ytdlp_ok = False
    
    return jsonify({
        'ffmpeg': ffmpeg_ok,
        'yt_dlp': ytdlp_ok,
        'groq_api': bool(os.getenv('GROQ_API_KEY')),
        'videos_used': db.get_used_videos_count()
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Main video generation endpoint"""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        duration = int(data.get('duration', DEFAULT_FINAL_DURATION))
        
        if not topic:
            return jsonify({'error': 'Topic required'}), 400
        
        if duration < 10 or duration > 300:
            return jsonify({'error': 'Duration must be 10-300 seconds'}), 400
        
        logger.info(f"Starting generation: topic={topic}, duration={duration}s")
        
        # Step 1: Generate search keywords
        logger.info("Step 1: Generating keywords...")
        keywords = groq.generate_search_keywords(topic)
        
        if not keywords:
            keywords = [topic]
        
        # Step 2: Find and download videos
        logger.info("Step 2: Searching and downloading videos...")
        clips = []
        clips_needed = (duration // CLIP_DURATION) + 1  # Extra clips for flexibility
        
        for keyword in keywords:
            if len(clips) >= clips_needed:
                break
            
            videos = youtube.search_videos(keyword, max_results=3)
            
            for video in videos:
                if len(clips) >= clips_needed:
                    break
                
                # Check if already used
                if db.is_video_used(video['id']):
                    continue
                
                logger.info(f"Downloading: {video['title']}")
                
                # Download video
                video_path = youtube.download_video(video['url'], video['id'])
                if not video_path:
                    continue
                
                # Get duration
                video_duration = processor.get_video_duration(video_path)
                if video_duration < CLIP_DURATION:
                    youtube.cleanup_temp_file(video_path)
                    continue
                
                # Check relevance
                if not groq.is_relevant(video['title'], topic):
                    youtube.cleanup_temp_file(video_path)
                    continue
                
                # Find best segment
                logger.info("Analyzing video...")
                analysis = groq.analyze_video_content(video['title'], topic)
                start_time = max(0, analysis.get('best_start_second', 0))
                
                # Extract clip
                clip_path = TEMP_DIR / f"clip_{video['id']}.mp4"
                if processor.extract_clip(video_path, start_time, CLIP_DURATION, str(clip_path)):
                    clips.append({
                        'path': str(clip_path),
                        'video_id': video['id'],
                        'title': video['title']
                    })
                    
                    # Mark as used
                    db.add_used_video(video['id'], 'youtube', video['title'], video['url'])
                
                # Cleanup original video
                youtube.cleanup_temp_file(video_path)
        
        if not clips:
            return jsonify({'error': 'No suitable videos found'}), 400
        
        logger.info(f"Found {len(clips)} clips, needed {clips_needed}")
        
        # Step 3: Generate script and voice
        logger.info("Step 3: Generating script and voice...")
        script = groq.generate_script(topic, clips[0]['title'])
        
        audio_path = TEMP_DIR / "voiceover.mp3"
        if not voice.generate_speech(script, str(audio_path)):
            return jsonify({'error': 'Voice generation failed'}), 500
        
        # Step 4: Add voice to first clip
        logger.info("Step 4: Adding voice overlay...")
        voiced_clip = TEMP_DIR / "voiced_clip.mp4"
        if not processor.add_audio_overlay(clips[0]['path'], str(audio_path), str(voiced_clip)):
            return jsonify({'error': 'Audio overlay failed'}), 500
        
        # Step 5: Concatenate clips
        logger.info("Step 5: Concatenating clips...")
        video_list = [str(voiced_clip)] + [c['path'] for c in clips[1:]]
        
        output_file = UPLOAD_DIR / f"output_{Path(topic).stem}.mp4"
        if not processor.concatenate_videos(video_list, str(output_file)):
            return jsonify({'error': 'Video concatenation failed'}), 500
        
        logger.info(f"Video generated: {output_file}")
        
        # Cleanup temp files
        for clip in clips:
            youtube.cleanup_temp_file(clip['path'])
        youtube.cleanup_temp_file(str(audio_path))
        youtube.cleanup_temp_file(str(voiced_clip))
        
        return jsonify({
            'success': True,
            'file': output_file.name,
            'script': script,
            'clips_used': len(clips)
        })
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download(filename):
    """Download generated video"""
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(str(file_path), as_attachment=True)
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos')
def list_videos():
    """List generated videos"""
    try:
        videos = []
        for file in UPLOAD_DIR.glob('*.mp4'):
            videos.append({
                'name': file.name,
                'size': file.stat().st_size / (1024*1024),  # MB
                'created': file.stat().st_mtime
            })
        
        return jsonify({'videos': videos})
    except Exception as e:
        logger.error(f"List error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
