import os
from pathlib import Path

# ===== THƯ MỤC HỆ THỐNG =====
BASE_DIR = Path(__file__).parent.resolve()
TEMP_DIR = BASE_DIR / "temp" / "video_scraper"
UPLOAD_DIR = BASE_DIR / "videos"
DB_PATH = BASE_DIR / "used_videos.db"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ===== THIẾT LẬP CHẤT LƯỢNG HÌNH ẢNH (720p HD) =====
VIDEO_QUALITY = {
    'format': 'bv*[height<=720]+ba/b[height<=720]/b',
    'audio_format': 'bestaudio/best',
    'height': 720,
    'fps': 24,
}

FFMPEG_PRESET = 'veryfast'
FFMPEG_CRF = 23
FFMPEG_BITRATE_VIDEO = '2500k'
FFMPEG_BITRATE_AUDIO = '128k'

# ===== API KEYS & THỜI GIAN =====
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

CLIP_DURATION = 5  # Cắt cố định 5 giây mỗi cảnh
DEFAULT_FINAL_DURATION = 60
MIN_VIDEO_LENGTH = 15
MAX_VIDEO_LENGTH = 900

# ===== TỐI ƯU HÓA CHO TERMUX / ĐIỆN THOẠI =====
MAX_CONCURRENT_DOWNLOADS = 1
CLEANUP_AFTER_PROCESS = True
USE_CACHE = True
CACHE_EXPIRY = 3600

DOWNLOAD_TIMEOUT = 300
API_TIMEOUT = 30
PROCESSING_TIMEOUT = 900

# ===== CẤU HÌNH AI (GROQ) =====
GROQ_MODEL = 'qwen/qwen3.8-27b'
GROQ_TEMPERATURE = 0.6
GROQ_MAX_TOKENS = 1200

# ===== CẤU HÌNH GIỌNG ĐỌC THUYẾT MINH =====
TTS_LANGUAGE = 'en-US'
TTS_VOICE = 'en-US-ChristopherNeural'
TTS_SPEED = 1.0

# ===== CẤU HÌNH WEB APP =====
FLASK_DEBUG = False
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'app.log'
