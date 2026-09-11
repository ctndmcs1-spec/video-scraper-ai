import subprocess
import json
import os
from pathlib import Path
from config import TEMP_DIR, VIDEO_QUALITY, DOWNLOAD_TIMEOUT
from db import db
from groq_handler import groq
import logging

logger = logging.getLogger(__name__)

BANNED_KEYWORDS = [
    'news', 'interview', 'report', 'press', 'conference', 'briefing',
    'investigation', 'explained', 'analysis', 'lesson', 'presentation',
    'slide', 'powerpoint', 'atc', 'radar', 'reconstruction', 'reenactment',
    'simulation', 'simulator', 'animation', 'msfs', 'fs2020', 'x-plane', 'gta', 'cgi', '3d'
]

class YouTubeHandler:
    def __init__(self):
        self.temp_dir = TEMP_DIR
    
    def search_and_verify_videos(self, query, topic, max_results=15):
        """Quét danh sách và dùng AI thẩm định trước khi quyết định tải"""
        try:
            cleaned_query = f"{query} -news -interview -report -simulation -radar -atc -slide"
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '-j',
                f'ytsearch{max_results}:{cleaned_query}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=DOWNLOAD_TIMEOUT)
            if result.returncode != 0:
                return []
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        v = json.loads(line)
                        title = v.get('title', '')
                        desc = v.get('description', '')
                        uploader = v.get('uploader', '')
                        dur = v.get('duration', 0)
                        
                        # Lọc thô từ khóa cấm
                        if any(bad in title.lower() for bad in BANNED_KEYWORDS) or any(bad in uploader.lower() for bad in ['news', 'media', 'investigation', 'channel 4', 'abc']):
                            continue
                        
                        if dur < 25 or db.is_video_used(v['id']):
                            continue

                        # Thẩm định bằng AI Groq
                        logger.info(f"AI đang thẩm định video: {title[:50]}...")
                        if not groq.verify_video_authenticity(title, desc, uploader, topic):
                            logger.info(f"--> AI đã loại bỏ (Video thời sự/phỏng vấn): {title[:50]}")
                            continue

                        logger.info(f"--> AI chấp nhận: {title[:50]}")
                        videos.append({
                            'id': v['id'],
                            'title': title,
                            'url': v.get('webpage_url', ''),
                            'duration': dur,
                        })
                    except Exception:
                        pass
            return videos
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm YouTube: {e}")
            return []
    
    def calculate_clip_timestamps(self, duration, clip_len=5, min_gap=25):
        usable_start = 15.0
        usable_end = max(usable_start + clip_len, duration - 10.0)
        usable_len = usable_end - usable_start
        
        if usable_len < clip_len:
            return [usable_start]
        
        possible_clips = min(4, int(usable_len // (clip_len + min_gap)) + 1)
        if possible_clips <= 1:
            return [usable_start + (usable_len * 0.35)]
        
        timestamps = []
        step = usable_len / possible_clips
        for i in range(possible_clips):
            t = usable_start + (i * step)
            if t + clip_len <= duration:
                timestamps.append(round(t, 1))
        
        return timestamps

    def download_video(self, video_url, video_id):
        try:
            output_path = self.temp_dir / f"{video_id}.mp4"
            if output_path.exists():
                return str(output_path)
            
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '-f', VIDEO_QUALITY['format'],
                '--merge-output-format', 'mp4',
                '-o', str(output_path),
                video_url
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=DOWNLOAD_TIMEOUT)
            if res.returncode == 0 and output_path.exists():
                return str(output_path)
            return None
        except Exception as e:
            logger.error(f"Lỗi tải video: {e}")
            return None
    
    def cleanup_temp_file(self, video_path):
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                return True
        except Exception:
            return False

youtube = YouTubeHandler()
