import sqlite3
from pathlib import Path
from config import DB_PATH
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(str(self.db_path))

    def init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS used_videos (
                        id TEXT PRIMARY KEY,
                        source TEXT,
                        title TEXT,
                        url TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Lỗi khởi tạo DB: {e}")

    def is_video_used(self, video_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM used_videos WHERE id = ?', (video_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Lỗi kiểm tra trùng video: {e}")
            return False

    def add_used_video(self, video_id, source, title, url):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO used_videos (id, source, title, url)
                    VALUES (?, ?, ?, ?)
                ''', (video_id, source, title, url))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Lỗi lưu video vào DB: {e}")
            return False

    def get_used_videos_count(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM used_videos')
                res = cursor.fetchone()
                return res[0] if res else 0
        except Exception as e:
            logger.error(f"Lỗi đếm số video đã dùng: {e}")
            return 0

db = Database()
