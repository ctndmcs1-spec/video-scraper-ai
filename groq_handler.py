import json
import logging
import os
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, GROQ_MAX_TOKENS

logger = logging.getLogger(__name__)

class GroqHandler:
    def __init__(self):
        self.api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.model = GROQ_MODEL or "qwen/qwen3.8-27b"
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _call_api(self, prompt, temperature=0.6, max_tokens=1000):
        key = os.getenv("GROQ_API_KEY") or self.api_key
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        res = requests.post(self.url, headers=headers, json=payload, timeout=35)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()

    def verify_video_authenticity(self, title, description, channel, topic):
        """Dung AI tham dinh xem video co phai quay thuc te hay la ban tin thoi su/phong van"""
        prompt = f"""
You are a video content filter verifying footage for a documentary compilation about: "{topic}".
Analyze this YouTube video metadata:
- Title: {title}
- Channel: {channel}
- Description: {description[:400]}

Criteria:
1. ACCEPT only if it is real-life caught-on-camera raw footage, deck cam, dashcam, cockpit, or bystander footage.
2. REJECT if it is a TV news report, interview, press conference, talk show, documentary with talking heads/hosts, animated explainer, or 3D simulation.

Reply with EXACTLY ONE word: ACCEPT or REJECT.
"""
        try:
            decision = self._call_api(prompt, temperature=0.1, max_tokens=10)
            return "ACCEPT" in decision.upper()
        except Exception as e:
            logger.warning(f"Loi tham dinh AI: {e}")
            return True

    def generate_search_keywords(self, topic):
        try:
            prompt = f"""
Given the topic: "{topic}".
Generate 4 realistic YouTube search queries to find real dashcam, raw CCTV, or eyewitness footage of this exact event.
DO NOT include words like: simulation, animation, video game, news, report, interview, slide, cgi.
Return ONLY a valid JSON list of 4 strings.
Example: ["cargo ship heavy storm rogue wave", "ship violently rocking extreme sea raw footage"]
"""
            text = self._call_api(prompt, max_tokens=250)
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            queries = json.loads(text)
            if isinstance(queries, list) and len(queries) > 0:
                return queries
        except Exception:
            pass
        
        return [
            f"{topic} raw footage caught on camera",
            f"{topic} extreme close call seconds before disaster",
            f"{topic} real rough sea deck view",
            f"{topic} caught on camera"
        ]

    def generate_full_script(self, topic, target_duration):
        words_needed = int(target_duration * 2.3)
        topic_lower = topic.lower()
        strict_context = ""
        if any(w in topic_lower for w in ['ship', 'boat', 'sea', 'ocean', 'wave', 'storm', 'water', 'sailor']):
            strict_context = "CRITICAL INSTRUCTION: This documentary is STRICTLY about MARITIME STORMS, SHIPS, GIANT WAVES, AND THE SEA. DO NOT mention airplanes, pilots, runways, flight, altitude, or aviation."
        elif any(w in topic_lower for w in ['plane', 'aviation', 'flight', 'landing', 'pilot', 'cockpit', 'aircraft']):
            strict_context = "CRITICAL INSTRUCTION: This documentary is STRICTLY about AVIATION, PLANES, AND EMERGENCY LANDINGS. DO NOT mention ships, ocean vessels, or maritime disasters."

        prompt = f"""
You are the master narrator of a world-class documentary series.
Write a continuous, dramatic, and immersive English narration script for a {int(target_duration)}-second video compilation about: "{topic}".

{strict_context}

Script Requirements:
1. Target length: EXACTLY around {words_needed} words to match the {int(target_duration)}-second timeline.
2. Tone: Suspenseful, authoritative, intense, and cinematic.
3. Content: Describe the sheer power of nature or physics, the extreme tension of the situation, the split-second decisions made under immense pressure, and the fight for survival.
4. Format: PURE SPOKEN NARRATION ONLY. 
   - DO NOT include scene directions, narrator labels (e.g. "Narrator:"), SFX cues, music tags [SFX], quotation marks, or emojis.
   - Flow smoothly like one continuous spoken story from sentence 1 to the end.
"""
        try:
            script = self._call_api(prompt, max_tokens=GROQ_MAX_TOKENS)
            lines = [line.strip() for line in script.split("\n") if line.strip() and not line.strip().startswith(("[", "(", "Narrator"))]
            cleaned_script = " ".join(lines).replace('"', '').replace('*', '')
            if len(cleaned_script) > 50:
                return cleaned_script
        except Exception as e:
            logger.error(f"Lỗi tạo kịch bản từ Groq: {e}")

        if "ship" in topic_lower or "sea" in topic_lower or "wave" in topic_lower:
            return (
                "The ocean is an unpredictable force capable of testing the limits of human engineering and courage. "
                "In the open waters, violent storms arise without mercy, throwing massive walls of water against steel hulls. "
                "Every roll of the deck and every crushing impact of a rogue wave pushes the vessel closer to the edge. "
                "These raw recordings capture the unbelievable moments where sailors faced nature at its most furious, "
                "fighting through towering swells and relentless gales where survival depended on every single second."
            )
        else:
            return (
                "High above the earth, extreme situations demand split-second precision where there is zero margin for error. "
                "When critical mechanical failures strike or sudden violent turbulence attacks, modern aircraft are pushed beyond design limits. "
                "Witness the gripping seconds caught on camera where disaster confronted sheer human resilience. "
                "From hair-raising crosswind approaches to unbelievable emergency landings, these moments show what happens "
                "when courage and physics collide in the most dangerous environments on the planet."
            )

groq = GroqHandler()
