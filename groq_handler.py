import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS
from db import db
import logging

logger = logging.getLogger(__name__)

class GroqHandler:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
    
    def generate_search_keywords(self, topic):
        """Generate diverse search keywords from topic using Groq"""
        cache_key = f"keywords_{topic}"
        cached = db.get_cache(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            prompt = f"""
            Generate 5 diverse and specific YouTube search keywords for the topic: "{topic}"
            
            Requirements:
            - Make keywords natural and realistic
            - Mix broad and specific searches
            - Include variations and related terms
            - Format as JSON array only
            
            Example output:
            ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5"]
            
            Output ONLY the JSON array, no other text.
            """
            
            message = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS,
            )
            
            response_text = message.content[0].text.strip()
            keywords = json.loads(response_text)
            
            # Cache result
            db.set_cache(cache_key, json.dumps(keywords))
            
            logger.info(f"Generated keywords: {keywords}")
            return keywords
        
        except Exception as e:
            logger.error(f"Groq keywords error: {e}")
            return [topic]  # Fallback to original topic
    
    def analyze_video_content(self, transcript, topic):
        """Analyze video to find best matching segment"""
        try:
            prompt = f"""
            Analyze this video transcript and find the BEST 5-second segment that matches the topic: "{topic}"
            
            Transcript:
            {transcript}
            
            Response format (JSON only):
            {{
                "best_start_second": <number>,
                "relevance_score": <0-100>,
                "reasoning": "<brief explanation>"
            }}
            
            Output ONLY valid JSON, no other text.
            """
            
            message = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=GROQ_TEMPERATURE,
                max_tokens=500,
            )
            
            response_text = message.content[0].text.strip()
            result = json.loads(response_text)
            
            return result
        
        except Exception as e:
            logger.error(f"Groq analysis error: {e}")
            return {
                "best_start_second": 0,
                "relevance_score": 50,
                "reasoning": "Error in analysis, using default"
            }
    
    def generate_script(self, topic, video_title, context=""):
        """Generate AI script for voiceover"""
        cache_key = f"script_{topic}_{video_title}"
        cached = db.get_cache(cache_key)
        if cached:
            return cached
        
        try:
            prompt = f"""
            Write a SHORT, engaging 15-20 second voiceover script for a video about: {topic}
            
            Video: {video_title}
            Context: {context}
            
            Requirements:
            - Keep it SHORT (15-20 seconds when read aloud)
            - Use conversational tone
            - No special characters or emojis
            - Make it engaging and informative
            - Natural flow
            
            Output ONLY the script text, nothing else.
            """
            
            message = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=GROQ_TEMPERATURE,
                max_tokens=300,
            )
            
            script = message.content[0].text.strip()
            
            # Cache result
            db.set_cache(cache_key, script)
            
            logger.info(f"Generated script: {script[:50]}...")
            return script
        
        except Exception as e:
            logger.error(f"Groq script error: {e}")
            return f"Check out this amazing video about {topic}. Don't miss it!"
    
    def is_relevant(self, video_title, topic):
        """Quick check if video is relevant to topic"""
        try:
            prompt = f"""
            Is this video title relevant to the topic "{topic}"?
            
            Video title: "{video_title}"
            
            Answer with only: YES or NO
            """
            
            message = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10,
            )
            
            response = message.content[0].text.strip().upper()
            return "YES" in response
        
        except Exception as e:
            logger.error(f"Relevance check error: {e}")
            return True  # Default to relevant if error

# Global instance
groq = GroqHandler()
