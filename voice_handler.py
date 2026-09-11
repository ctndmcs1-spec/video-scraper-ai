import asyncio
import os
import logging
from pathlib import Path
import edge_tts
from config import TTS_VOICE

logger = logging.getLogger(__name__)

class VoiceHandler:
    def __init__(self):
        self.voice = TTS_VOICE or "vi-VN-HoaiMyNeural"
    
    def generate_speech(self, text, output_file):
        try:
            out_path = Path(output_file).resolve()
            
            async def _run():
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(str(out_path))

            asyncio.run(_run())
            
            if out_path.exists() and out_path.stat().st_size > 0:
                logger.info(f"TTS generated: {out_path}")
                return str(out_path)
            
            logger.error("TTS generation failed: Empty file")
            return None
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            return None

voice = VoiceHandler()
