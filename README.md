# 🎬 Video Scraper AI - Termux Edition

AI-powered video scraper that automatically finds, cuts, and combines YouTube videos based on keywords. Runs on Android via Termux with Groq AI for intelligent analysis.

## ✨ Features

- 🔍 **Smart Search**: Uses Groq AI to generate diverse search keywords
- 🎯 **Intelligent Cutting**: AI analyzes videos to find the most relevant 5-second segments
- 🗣️ **AI Voice**: Generates voiceover scripts and synthesizes speech
- 🎞️ **Auto-Merge**: Combines clips into final video with customizable duration
- 📱 **Termux Optimized**: Runs efficiently on Android phones
- 💾 **No Duplicates**: Tracks used videos to prevent repetition
- 🌐 **Web UI**: Beautiful interface with slider for duration control
- ⚡ **Lightweight**: 480p video quality, optimized for mobile

## 📋 Requirements

### Termux Dependencies
```bash
# FFmpeg + yt-dlp + Python
pkg install ffmpeg python

# Additional build tools (for numpy/scipy)
pkg install clang fftpack
```

### Python Packages
```bash
pip install -r requirements.txt
```

### Environment Variables
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

Get your free Groq API key: https://console.groq.com

## 🚀 Quick Start on Termux

### Step 1: Setup Termux (First Time)
```bash
# Update packages
pkg update && pkg upgrade

# Install dependencies
pkg install git python ffmpeg

# Clone repository
git clone https://github.com/ctndmcs1-spec/video-scraper-ai
cd video-scraper-ai

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Set API Key
```bash
# Option A: Set environment variable (temporary)
export GROQ_API_KEY="gsk_your_key_here"

# Option B: Add to .bashrc (permanent)
echo 'export GROQ_API_KEY="gsk_your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Run Application
```bash
python main.py
```

You should see:
```
Starting Flask app on 0.0.0.0:5000
WARNING in app.run... Use a production WSGI server instead.
```

### Step 4: Access Web UI
**On your phone browser:**
- Open: `http://localhost:5000`
- Or: `http://127.0.0.1:5000`

### Step 5: Generate Videos
1. Enter topic (e.g., "motivational quotes")
2. Drag slider to set duration (10-300 seconds)
3. Click "Generate Video 🚀"
4. Wait for processing
5. Download when done

## 🎮 How It Works

```
Input: "Funny Cat Videos" + 60 seconds
    ↓
[Groq AI] Generate keywords: 
  - "funny cats"
  - "cat fails"
  - "cute kittens"
    ↓
[YouTube] Search & download videos (480p)
    ↓
[Groq AI] Analyze each video for relevance
    ↓
[FFmpeg] Extract best 5-second segments
    ↓
[Groq AI] Generate voiceover script
    ↓
[TTS] Create voice audio
    ↓
[FFmpeg] Add voice overlay to first clip
    ↓
[FFmpeg] Concatenate all clips
    ↓
Output: 60-second video with AI narration
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Video quality (480p for Termux)
VIDEO_QUALITY = {
    'format': 'best[height<=480]',  # Max 480p
}

# FFmpeg optimization
FFMPEG_PRESET = 'veryfast'  # ultrafast/superfast/veryfast/fast
FFMPEG_CRF = 26  # 0-51, higher = lower quality but faster

# Video settings
CLIP_DURATION = 5  # Seconds per clip
DEFAULT_FINAL_DURATION = 60  # Default video length
MIN_VIDEO_LENGTH = 10
MAX_VIDEO_LENGTH = 300

# Groq AI
GROQ_MODEL = 'mixtral-8x7b-32768'
GROQ_TEMPERATURE = 0.7

# TTS Voice
TTS_LANGUAGE = 'en-US'
```

## 🛠️ Troubleshooting

### Issue: "FFmpeg not found"
```bash
pkg install ffmpeg
```

### Issue: "yt-dlp not found"
```bash
pip install yt-dlp --upgrade
```

### Issue: "Groq API Error"
- Check your API key: `echo $GROQ_API_KEY`
- Get free key: https://console.groq.com
- API might be rate limited - wait 5 minutes

### Issue: "Video generation slow"
- Check RAM: `free -h`
- Close other apps on phone
- Reduce duration or quality in config.py
- Check internet connection

### Issue: "Out of storage"
- Generated videos saved in `videos/` folder
- Temp files in `/tmp/` (auto-deleted)
- Delete old videos: `rm videos/*.mp4`

### Issue: "Permission denied" errors
```bash
chmod +x main.py
```

## 📁 Project Structure

```
video-scraper-ai/
├── main.py                 # Flask app (main entry point)
├── config.py              # Configuration
├── groq_handler.py        # Groq AI integration
├── youtube_handler.py     # YouTube download & search
├── video_processor.py     # FFmpeg video manipulation
├── voice_handler.py       # Text-to-speech
├── db.py                  # SQLite database
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Web UI
├── videos/                # Generated videos
├── used_videos.db         # Tracks used videos
└── app.log                # Application logs
```

## 🔐 Privacy & Legal

⚠️ **Important:**
- Only download videos you have permission to use
- Respect YouTube Terms of Service
- Use for educational/personal projects only
- Check copyright before using video content
- Rate limiting: Don't abuse API requests

## 💡 Tips for Best Results

1. **Specific Keywords**: "motivational quotes morning" works better than just "motivation"
2. **Optimal Duration**: 30-120 seconds works best
3. **Test Topics First**: Try with common topics to understand output
4. **Monitor Logs**: Check `app.log` for errors
5. **Clear Cache**: Delete old videos if storage is low
6. **Groq Rate Limit**: Free tier has limits, spread requests

## 📊 Performance on Termux

| Task | Time | Notes |
|------|------|-------|
| Search videos | 30-60s | Depends on internet |
| Download (480p) | 30-60s | Depends on video length |
| Analyze with Groq | 10-20s | API call |
| Extract clip | 15-30s | FFmpeg processing |
| TTS generation | 5-10s | Depends on script length |
| Concatenate videos | 20-60s | FFmpeg encoding |
| **Total (per video)** | **2-3 min** | 10 videos = 20-30 min |

## 🚀 Advanced: Run as Background Service

```bash
# Install screen (persistent terminal)
pkg install screen

# Start in new screen session
screen -S scraper python main.py

# Detach: Ctrl+A then D
# Reattach: screen -r scraper
# List sessions: screen -ls
```

## 📝 Common Issues & Solutions

### "Too many requests" from Groq
```python
# Edit config.py
CACHE_EXPIRY = 7200  # Increase to 2 hours
USE_CACHE = True  # Make sure caching is on
```

### Videos are too dark/blurry
```python
# Edit config.py
FFMPEG_CRF = 23  # Lower number = better quality (but slower)
```

### Video generation stuck
```bash
# Kill and restart
ps aux | grep python
kill <PID>
python main.py
```

## 🤝 Contributing

Found a bug? Want to improve it?
1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - Feel free to use and modify

## 🎯 Roadmap

- [ ] TikTok support
- [ ] Instagram Reels support
- [ ] Multiple voice options
- [ ] Custom backgrounds/overlays
- [ ] Real-time progress notifications
- [ ] Batch processing multiple topics
- [ ] Video watermarking
- [ ] Automatic social media upload

## 💬 Support

Issues? Questions?
1. Check logs: `cat app.log`
2. Read README again
3. Google the error message
4. Create GitHub issue with:
   - Error message
   - Steps to reproduce
   - Termux version
   - Phone specs

## 🎉 Credits

Built with:
- [Groq API](https://groq.com) - Fast LLM inference
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download
- [FFmpeg](https://ffmpeg.org) - Video processing
- [Flask](https://flask.palletsprojects.com) - Web framework
- [edge-tts](https://github.com/rany2/edge-tts) - Text-to-speech

---

**Made for Android with ❤️ on Termux**

*Last updated: 2026-09-11*
