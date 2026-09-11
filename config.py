import os
from pathlib import Path

# ===== PATHS =====
BASE_DIR = Path(__file__).parent
TEMP_DIR = Path("/tmp/video_scraper")  # Use /tmp for faster I/O
UPLOAD_DIR = BASE_DIR / "videos"
DB_PATH = BASE_DIR / "used_videos.db"

# Create directories if they don't exist
TEMP_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ===== VIDEO OPTIMIZATION =====
# Tối ưu cho Termux: độ phân giải 480p, bitrate thấp
VIDEO_QUALITY = {
    'format': 'best[height<=480]',  # Max 480p
    'audio_format': 'bestaudio/best',
    'height': 480,
    'fps': 24,  # 30fps -> 24fps để tiết kiệm
}

# FFmpeg encoding (tối ưu tốc độ vs chất lượng)
FFMPEG_PRESET = 'veryfast'  # ultrafast/superfast/veryfast/fast
FFMPEG_CRF = 26  # 0-51, cao hơn = chất lượng thấp hơn nhưng nhanh hơn
FFMPEG_BITRATE_VIDEO = '800k'  # 1000k -> 800k
FFMPEG_BITRATE_AUDIO = '96k'   # 128k -> 96k

# ===== API KEYS =====
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GOOGLE_TTS_CREDENTIALS = os.getenv('GOOGLE_TTS_JSON', '')

# ===== VIDEO SETTINGS =====
CLIP_DURATION = 5  # Seconds per clip
DEFAULT_FINAL_DURATION = 60  # Default video length in seconds
MIN_VIDEO_LENGTH = 10  # Minimum video length
MAX_VIDEO_LENGTH = 300  # Max 5 minutes

# ===== TERMUX OPTIMIZATION =====
MAX_CONCURRENT_DOWNLOADS = 1  # 1 video at a time (RAM saver)
CLEANUP_AFTER_PROCESS = True  # Delete temp files after processing
USE_CACHE = True  # Cache Groq API results
CACHE_EXPIRY = 3600  # 1 hour

# ===== TIMEOUTS =====
DOWNLOAD_TIMEOUT = 300  # 5 minutes
API_TIMEOUT = 30  # 30 seconds
PROCESSING_TIMEOUT = 600  # 10 minutes

# ===== GROQ SETTINGS =====
GROQ_MODEL = 'mixtral-8x7b-32768'  # Fast & accurate
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1000

# ===== TTS SETTINGS =====
TTS_LANGUAGE = 'en-US'
TTS_VOICE = 'en-US-Neural2-C'  # Google Cloud TTS voice
TTS_SPEED = 1.0

# ===== WEB APP =====
FLASK_DEBUG = False
FLASK_HOST = '0.0.0.0'  # Listen on all interfaces (access from browser)
FLASK_PORT = 5000

# ===== LOGGING =====
LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'app.log'
