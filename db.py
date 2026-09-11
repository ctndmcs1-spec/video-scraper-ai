import sqlite3
from datetime import datetime
from config import DB_PATH
import logging

logger = logging.getLogger(__name__)

class VideoDatabase:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize database if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS used_videos (
                    id INTEGER PRIMARY KEY,
                    video_id TEXT UNIQUE NOT NULL,
                    platform TEXT NOT NULL,
                    title TEXT,
                    url TEXT,
                    used_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
    
    def add_used_video(self, video_id, platform, title='', url=''):
        """Add video to used list"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO used_videos (video_id, platform, title, url)
                VALUES (?, ?, ?, ?)
            ''', (video_id, platform, title, url))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding video: {e}")
            return False
    
    def is_video_used(self, video_id):
        """Check if video already used"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM used_videos WHERE video_id = ?', (video_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            logger.error(f"Error checking video: {e}")
            return False
    
    def get_used_videos_count(self):
        """Get total used videos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM used_videos')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
    
    def set_cache(self, key, value):
        """Cache API results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO cache (key, value)
                VALUES (?, ?)
            ''', (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Cache error: {e}")
            return False
    
    def get_cache(self, key):
        """Get cached value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM cache WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

# Global instance
db = VideoDatabase()
