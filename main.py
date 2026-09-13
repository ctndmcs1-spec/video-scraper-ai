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

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1500 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'ffmpeg': True,
        'yt_dlp': True,
        'groq_api': bool(os.getenv('GROQ_API_KEY')),
        'videos_used': db.get_used_videos_count()
    })

@app.route('/api/generate', methods=['POST'])
def generate_video():
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        duration = int(data.get('duration', DEFAULT_FINAL_DURATION))
        
        if not topic:
            return jsonify({'error': 'Vui lòng nhập chủ đề video'}), 400
        
        logger.info(f"Bắt đầu quy trình: Chủ đề='{topic}', Thời lượng mục tiêu={duration}s")
        
        # 1. Lấy danh sách từ khóa tìm kiếm
        search_queries = groq.generate_search_keywords(topic)
        
        clip_len = CLIP_DURATION  # Cố định 5 giây
        clips_needed = (duration // clip_len)
        clips = []
        
        # 2. Quét video và cắt nhiều đoạn 5s cách quãng trên mỗi video
        for q in search_queries:
            if len(clips) >= clips_needed:
                break
            videos = youtube.search_videos(q, max_results=60)
            
            for v in videos:
                if len(clips) >= clips_needed:
                    break
                if db.is_video_used(v['id']):
                    continue
                
                v_path = youtube.download_video(v['url'], v['id'])
                if not v_path:
                    continue
                
                v_dur = processor.get_duration(v_path)
                timestamps = youtube.calculate_clip_timestamps(v_dur, clip_len=clip_len, min_gap=25)
                
                extracted_any = False
                for idx, t_sec in enumerate(timestamps):
                    if len(clips) >= clips_needed:
                        break
                    
                    clip_path = TEMP_DIR / f"clip_{v['id']}_{idx}.mp4"
                    if processor.extract_clip(v_path, t_sec, clip_len, str(clip_path)):
                        clips.append({'path': str(clip_path)})
                        extracted_any = True
                
                if extracted_any:
                    db.add_used_video(v['id'], 'youtube', v['title'], v['url'])
                
                youtube.cleanup_temp_file(v_path)
        
        if not clips:
            return jsonify({'error': 'Không thu thập được clip nào phù hợp'}), 400
        
        logger.info(f"Đã thu thập thành công {len(clips)} clip 5s. Đang ghép video...")
        
        # 3. Nối các đoạn clip lại với nhau
        raw_concat = TEMP_DIR / "raw_concat.mp4"
        video_paths = [c['path'] for c in clips]
        processor.concatenate_videos(video_paths, str(raw_concat))
        
        actual_total_dur = processor.get_duration(str(raw_concat))
        
        # 4. Viết kịch bản chuẩn chủ đề và tạo voiceover
        logger.info(f"Đang sinh kịch bản thuyết minh cho {actual_total_dur:.1f} giây...")
        script = groq.generate_full_script(topic, actual_total_dur)
        
        audio_path = TEMP_DIR / "full_voiceover.mp3"
        voice.generate_speech(script, str(audio_path))
        
        # 5. Phủ âm thanh và đồng bộ nhịp đọc khớp với video
        clean_name = "".join([c if c.isalnum() else "_" for c in topic])[:40]
        output_file = UPLOAD_DIR / f"final_{clean_name}.mp4"
        processor.sync_and_overlay_audio(str(raw_concat), str(audio_path), str(output_file))
        
        # 6. Dọn dẹp sạch sẽ các tệp tạm để giải phóng bộ nhớ máy
        for c in clips:
            youtube.cleanup_temp_file(c['path'])
        youtube.cleanup_temp_file(str(raw_concat))
        youtube.cleanup_temp_file(str(audio_path))
        
        return jsonify({
            'success': True,
            'file': output_file.name,
            'script': script,
            'clips_used': len(clips)
        })
    except Exception as e:
        logger.error(f"Lỗi trong quá trình tạo video: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>')
def download(filename):
    """Xử lý nút tải video trực tiếp về trình duyệt"""
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File không tồn tại'}), 404
        return send_file(str(file_path.resolve()), as_attachment=True)
    except Exception as e:
        logger.error(f"Lỗi tải file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
