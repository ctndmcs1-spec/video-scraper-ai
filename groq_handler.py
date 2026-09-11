import json
import logging
import os
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS
from db import db

logger = logging.getLogger(__name__)

class GroqHandler:
    def __init__(self):
        self.api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.model = GROQ_MODEL
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _call_api(self, prompt, temperature=None, max_tokens=None):
        api_key = os.getenv("GROQ_API_KEY") or self.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else GROQ_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens is not None else GROQ_MAX_TOKENS
        }
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    
    def generate_search_keywords(self, topic):
        cache_key = f"keywords_{topic}"
        cached = db.get_cache(cache_key)
        if cached:
            return json.loads(cached)
        
        try:
            prompt = f'Generate 3 diverse YouTube search keywords for topic: "{topic}". Return ONLY a JSON array of strings, e.g. ["keyword 1", "keyword 2"].'
            text = self._call_api(prompt)
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            keywords = json.loads(text)
            db.set_cache(cache_key, json.dumps(keywords))
            return keywords
        except Exception as e:
            logger.error(f"Groq keywords error: {e}")
            return [topic]
    
    def analyze_video_content(self, transcript, topic):
        return {
            "best_start_second": 0,
            "relevance_score": 80,
            "reasoning": "Default segment"
        }
    
    def generate_script(self, topic, video_title, context=""):
        cache_key = f"script_{topic}_{video_title}"
        cached = db.get_cache(cache_key)
        if cached:
            return cached
        
        try:
            prompt = f'Viết một đoạn bình luận ngắn, lôi cuốn bằng tiếng Việt (khoảng 20-30 từ) cho video chủ đề "{topic}". Chỉ xuất ra văn bản lời thoại.'
            script = self._call_api(prompt, max_tokens=300)
            db.set_cache(cache_key, script)
            return script
        except Exception as e:
            logger.error(f"Groq script error: {e}")
            return f"Video tổng hợp những cảnh ấn tượng nhất về chủ đề {topic}."
    
    def is_relevant(self, video_title, topic):
        return True

groq = GroqHandler()
