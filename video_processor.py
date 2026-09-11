import subprocess
import os
from pathlib import Path
from config import (
    TEMP_DIR, FFMPEG_PRESET, FFMPEG_CRF, 
    FFMPEG_BITRATE_VIDEO, FFMPEG_BITRATE_AUDIO, CLIP_DURATION
)
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = TEMP_DIR
    
    def extract_clip(self, video_path, start_time, duration, output_path):
        """Extract 5-second clip from video"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', FFMPEG_PRESET,
                '-crf', str(FFMPEG_CRF),
                '-c:a', 'aac',
                '-b:a', FFMPEG_BITRATE_AUDIO,
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Extracted clip: {output_path}")
                return True
            else:
                logger.error(f"Clip extraction failed: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            logger.error(f"Extract clip error: {e}")
            return False
    
    def add_audio_overlay(self, video_path, audio_path, output_path):
        """Overlay voice narration on video (underlay video)"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]',
                '-map', '0:v',
                '-map', '[a]',
                '-c:v', 'libx264',
                '-preset', FFMPEG_PRESET,
                '-crf', str(FFMPEG_CRF),
                '-c:a', 'aac',
                '-b:a', FFMPEG_BITRATE_AUDIO,
                '-ac', '2',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Audio overlay added: {output_path}")
                return True
            else:
                logger.error(f"Audio overlay failed: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            logger.error(f"Audio overlay error: {e}")
            return False
    
    def concatenate_videos(self, video_list, output_path):
        """Merge multiple video clips into one"""
        try:
            # Create concat demuxer file
            concat_file = self.temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for video in video_list:
                    f.write(f"file '{video}'\n")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264',
                '-preset', FFMPEG_PRESET,
                '-crf', str(FFMPEG_CRF),
                '-c:a', 'aac',
                '-b:a', FFMPEG_BITRATE_AUDIO,
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300
            )
            
            # Cleanup concat file
            if concat_file.exists():
                os.remove(concat_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Videos concatenated: {output_path}")
                return True
            else:
                logger.error(f"Concatenation failed: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            logger.error(f"Concatenate error: {e}")
            return False
    
    def get_video_duration(self, video_path):
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
            else:
                logger.error(f"Duration retrieval failed")
                return 0
        
        except Exception as e:
            logger.error(f"Duration error: {e}")
            return 0
    
    def get_video_info(self, video_path):
        """Get video metadata"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate',
                '-of', 'json',
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                if data.get('streams'):
                    stream = data['streams'][0]
                    return {
                        'width': stream.get('width'),
                        'height': stream.get('height'),
                        'fps': stream.get('r_frame_rate', '30/1'),
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"Video info error: {e}")
            return None

# Global instance
processor = VideoProcessor()
