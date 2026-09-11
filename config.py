import os
from pathlib import Path

# ===== PATHS =====
BASE_DIR = Path(__file__).parent.resolve()
TEMP_DIR = BASE_DIR / "temp" / "video_scraper"
UPLOAD_DIR = BASE_DIR / "videos"
DB_PATH = BASE_DIR / "used_videos.db"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ===== VIDEO OPTIMIZATION =====
VIDEO_QUALITY = {
    'format': 'bv*[height<=480]+ba/b[height<=480]/b',
    'audio_format': 'bestaudio/best',
    'height': 480,
    'fps': 24,
}

FFMPEG_PRESET = 'veryfast'
FFMPEG_CRF = 26
FFMPEG_BITRATE_VIDEO = '800k'
FFMPEG_BITRATE_AUDIO = '96k'

# ===== API KEYS =====
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# ===== VIDEO SETTINGS =====
CLIP_DURATION = 5
DEFAULT_FINAL_DURATION = 60
MIN_VIDEO_LENGTH = 10
MAX_VIDEO_LENGTH = 300

# ===== TERMUX OPTIMIZATION =====
MAX_CONCURRENT_DOWNLOADS = 1
CLEANUP_AFTER_PROCESS = True
USE_CACHE = True
CACHE_EXPIRY = 3600

# ===== TIMEOUTS =====
DOWNLOAD_TIMEOUT = 300
API_TIMEOUT = 30
PROCESSING_TIMEOUT = 600

# ===== GROQ SETTINGS =====
GROQ_MODEL = 'openai/gpt-oss-120b'
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1000

# ===== TTS SETTINGS =====
TTS_LANGUAGE = 'vi-VN'
TTS_VOICE = 'vi-VN-HoaiMyNeural'
TTS_SPEED = 1.0

# ===== WEB APP =====
FLASK_DEBUG = False
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000

# ===== LOGGING =====
LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'app.log'
