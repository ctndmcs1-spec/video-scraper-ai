import subprocess
import os
from pathlib import Path
from config import TEMP_DIR, FFMPEG_PRESET, FFMPEG_CRF, FFMPEG_BITRATE_VIDEO, FFMPEG_BITRATE_AUDIO
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = TEMP_DIR

    def extract_clip(self, video_path, start_time, duration, output_path):
        try:
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', str(Path(video_path).resolve()),
                '-t', str(duration),
                '-c:v', 'libx264', '-preset', FFMPEG_PRESET, '-crf', str(FFMPEG_CRF),
                '-b:v', FFMPEG_BITRATE_VIDEO,
                '-c:a', 'aac', '-b:a', FFMPEG_BITRATE_AUDIO,
                '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-r', '24',
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=120)
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Lỗi trích xuất clip: {e}")
            return False

    def sync_and_overlay_audio(self, video_path, audio_path, output_path):
        """
        Dùng bộ lọc Karaoke/Center-Kill triệt tiêu giọng MC gốc ở kênh giữa,
        giữ nguyên âm thanh sóng biển/gió bão ở hai bên tai và phủ giọng đọc AI mới.
        """
        try:
            v_dur = self.get_duration(video_path)
            a_dur = self.get_duration(audio_path)
            
            speed_ratio = 1.0
            if a_dur > 0 and v_dur > 0:
                speed_ratio = a_dur / v_dur
                speed_ratio = max(0.85, min(1.25, speed_ratio))
            
            # Bộ lọc: 
            # 1. stereotools=mutec=true: Triệt tiêu âm thanh nằm chính giữa (giọng nói)
            # 2. equalizer giảm dải tần giọng người (800-2000Hz)
            # 3. Giữ lại âm trầm bass của sóng và gió ở mức 40%
            audio_filter = (
                f"[0:a]stereotools=mutec=true,equalizer=f=1200:t=q:w=1.5:g=-20,volume=0.4[bg];"
                f"[1:a]atempo={speed_ratio:.3f},volume=1.3[voice];"
                f"[bg][voice]amix=inputs=2:duration=first:dropout_transition=3[aout]"
            )
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(Path(video_path).resolve()),
                '-i', str(Path(audio_path).resolve()),
                '-filter_complex', audio_filter,
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', FFMPEG_BITRATE_AUDIO,
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=360)
            if res.returncode != 0:
                # Fallback nếu clip gốc là Mono (không có stereo để tách)
                fallback_filter = (
                    f"[0:a]equalizer=f=1000:t=q:w=2:g=-18,volume=0.15[bg];"
                    f"[1:a]atempo={speed_ratio:.3f},volume=1.3[voice];"
                    f"[bg][voice]amix=inputs=2:duration=first:dropout_transition=3[aout]"
                )
                cmd_fallback = [
                    'ffmpeg', '-y',
                    '-i', str(Path(video_path).resolve()),
                    '-i', str(Path(audio_path).resolve()),
                    '-filter_complex', fallback_filter,
                    '-map', '0:v',
                    '-map', '[aout]',
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    str(Path(output_path).resolve())
                ]
                res = subprocess.run(cmd_fallback, capture_output=True, timeout=360)

            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Lỗi xử lý âm thanh: {e}")
            return False

    def concatenate_videos(self, video_list, output_path):
        try:
            concat_file = self.temp_dir / "concat.txt"
            with open(concat_file, 'w', encoding='utf-8') as f:
                for v in video_list:
                    abs_v = Path(v).resolve().as_posix()
                    f.write(f"file '{abs_v}'\n")

            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file.resolve()),
                '-c:v', 'libx264', '-preset', FFMPEG_PRESET,
                '-b:v', FFMPEG_BITRATE_VIDEO,
                '-c:a', 'aac',
                str(Path(output_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, timeout=400)
            if concat_file.exists():
                os.remove(concat_file)
            return res.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Lỗi nối video: {e}")
            return False

    def get_duration(self, file_path):
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(Path(file_path).resolve())
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return float(res.stdout.strip()) if res.returncode == 0 else 0.0
        except Exception:
            return 0.0

processor = VideoProcessor()
