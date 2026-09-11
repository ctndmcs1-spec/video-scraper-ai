import subprocess
import os
from pathlib import Path
from config import TEMP_DIR, TTS_LANGUAGE, TTS_SPEED
import logging

logger = logging.getLogger(__name__)

class VoiceHandler:
    def __init__(self):
        self.temp_dir = TEMP_DIR
    
    def text_to_speech_google(self, text, output_file):
        """
        Google TTS using free edge-tts library (no API key needed)
        Install: pip install edge-tts
        """
        try:
            cmd = [
                'edge-tts',
                '--text', text,
                '--voice', 'en-US-AriaNeural',  # Natural sounding
                '--rate', f'+{int((TTS_SPEED - 1) * 50)}%',
                '--output-file', output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"TTS error: {result.stderr.decode()}")
                return False
            
            if os.path.exists(output_file):
                logger.info(f"TTS generated: {output_file}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return False
    
    def text_to_speech_pyttsx3(self, text, output_file):
        """
        Fallback: pyttsx3 (offline, no internet needed)
        Install: pip install pyttsx3
        """
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 1.0)  # Volume
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            if os.path.exists(output_file):
                logger.info(f"TTS generated (pyttsx3): {output_file}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"pyttsx3 TTS error: {e}")
            return False
    
    def generate_speech(self, text, output_file):
        """Generate speech audio from text"""
        try:
            # Try edge-tts first (better quality)
            if self.text_to_speech_google(text, output_file):
                return output_file
            
            # Fallback to pyttsx3
            if self.text_to_speech_pyttsx3(text, output_file):
                return output_file
            
            logger.error("All TTS methods failed")
            return None
        
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            return None

# Global instance
voice = VoiceHandler()
