import subprocess
import os
from pathlib import Path
from config import (
    TEMP_DIR, FFMPEG_PRESET, FFMPEG_CRF, 
    FFMPEG_BITRATE_VIDEO, FFMPEG_BITRATE_AUDIO
)
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = TEMP_DIR
    
    def extract_clip(self, video_path, start_time, duration, output_path):
        try:
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', str(Path(video_path).resolve()),
                '-t', str(duration),
                '-c:v', 'libx264', '-preset', FFMPEG_PRESET, '-crf', str(FFMPEG_CRF),
                '-c:a', 'aac', '-b:a', FFMPEG_BITRATE_AUDIO,
                '-vf', 'scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-r', '24',
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=120)
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Extract clip error: {e}")
            return False
    
    def add_audio_overlay(self, video_path, audio_path, output_path):
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', str(Path(video_path).resolve()),
                '-i', str(Path(audio_path).resolve()),
                '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=first[a]',
                '-map', '0:v',
                '-map', '[a]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', FFMPEG_BITRATE_AUDIO,
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=120)
            if res.returncode != 0:
                # Fallback neu clip goc khong co audio stream
                cmd_fallback = [
                    'ffmpeg', '-y',
                    '-i', str(Path(video_path).resolve()),
                    '-i', str(Path(audio_path).resolve()),
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-shortest',
                    str(Path(output_path).resolve())
                ]
                res = subprocess.run(cmd_fallback, capture_output=True, timeout=120)
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Audio overlay error: {e}")
            return False
    
    def concatenate_videos(self, video_list, output_path):
        try:
            concat_file = self.temp_dir / "concat.txt"
            with open(concat_file, 'w', encoding='utf-8') as f:
                for video in video_list:
                    # Ghi tuyet doi duong dan de FFmpeg khong bi nhan doi path
                    abs_v = Path(video).resolve().as_posix()
                    f.write(f"file '{abs_v}'\n")
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file.resolve()),
                '-c', 'copy',
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=300)
            
            if res.returncode != 0:
                # Fallback re-encode neu cac clip khac codec
                cmd_reencode = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file.resolve()),
                    '-c:v', 'libx264', '-preset', FFMPEG_PRESET,
                    '-c:a', 'aac',
                    str(Path(output_path).resolve())
                ]
                res = subprocess.run(cmd_reencode, capture_output=True, timeout=300)

            if concat_file.exists():
                os.remove(concat_file)
            
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Concatenate error: {e}")
            return False
    
    def get_video_duration(self, video_path):
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(Path(video_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return float(res.stdout.strip()) if res.returncode == 0 else 0.0
        except Exception:
            return 0.0

processor = VideoProcessor()
