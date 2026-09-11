import subprocess
import json
import os
from pathlib import Path
from config import TEMP_DIR, VIDEO_QUALITY, DOWNLOAD_TIMEOUT
from db import db
import logging

logger = logging.getLogger(__name__)

class YouTubeHandler:
    def __init__(self):
        self.temp_dir = TEMP_DIR
    
    def search_videos(self, query, max_results=5):
        """Search YouTube using yt-dlp (no API needed)"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                '-j',
                f'ytsearch{max_results}:{query}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DOWNLOAD_TIMEOUT
            )
            
            if result.returncode != 0:
                logger.error(f"Search error: {result.stderr}")
                return []
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        # Skip if already used
                        if not db.is_video_used(video['id']):
                            videos.append({
                                'id': video['id'],
                                'title': video.get('title', ''),
                                'url': video.get('webpage_url', ''),
                                'duration': video.get('duration', 0),
                            })
                    except:
                        pass
            
            logger.info(f"Found {len(videos)} videos for '{query}'")
            return videos
        
        except subprocess.TimeoutExpired:
            logger.error("Search timeout")
            return []
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def download_video(self, video_url, video_id):
        """Download video at 480p (optimized for Termux)"""
        try:
            output_path = self.temp_dir / f"{video_id}.mp4"
            
            if output_path.exists():
                logger.info(f"Video already downloaded: {output_path}")
                return str(output_path)
            
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '-f', VIDEO_QUALITY['format'],  # 480p max
                '-o', str(output_path),
                video_url
            ]
            
            logger.info(f"Downloading: {video_url}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=DOWNLOAD_TIMEOUT
            )
            
            if result.returncode != 0:
                logger.error(f"Download failed: {result.stderr.decode()}")
                return None
            
            if output_path.exists():
                logger.info(f"Downloaded: {output_path}")
                return str(output_path)
            else:
                logger.error("Download failed: file not created")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("Download timeout")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def get_video_info(self, video_url):
        """Get video metadata without downloading"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-warnings',
                video_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DOWNLOAD_TIMEOUT
            )
            
            if result.returncode != 0:
                return None
            
            info = json.loads(result.stdout)
            return {
                'id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration', 0),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail'),
            }
        
        except Exception as e:
            logger.error(f"Info retrieval error: {e}")
            return None
    
    def cleanup_temp_file(self, video_path):
        """Delete temp video file after processing"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.info(f"Cleaned up: {video_path}")
                return True
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        return False

# Global instance
youtube = YouTubeHandler()
