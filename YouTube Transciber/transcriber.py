import yt_dlp as youtube_dl
from transformers import pipeline
from datetime import timedelta
import os
from tqdm import tqdm
import logging

class YouTubeTranscriber:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_choices = {
            "Whisper Tiny": "openai/whisper-tiny",
            "Whisper Base": "openai/whisper-base", 
            "Whisper Small": "openai/whisper-small",
        }
        self.current_asr_model = None
        self.current_model_name = None
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)

    def load_asr_model(self, model_name):
        if self.current_model_name != model_name or self.current_asr_model is None:
            try:
                self.current_asr_model = pipeline(
                    "automatic-speech-recognition",
                    model=model_name,
                    device="cpu"
                )
                self.current_model_name = model_name
            except Exception as e:
                raise Exception(f"Failed to load ASR model: {str(e)}")

    def download_youtube_audio(self, url):
        audio_path = os.path.join(self.temp_dir, "audio.mp3")
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_path.replace('.mp3', ''),
            'quiet': True,
        }
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError("Download failed - no audio file created")
                
            return audio_path
            
        except Exception as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Failed to download audio: {str(e)}")

    def transcribe_audio(self, audio_file, model_name):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
        try:
            self.load_asr_model(model_name)
            
            with tqdm(total=os.path.getsize(audio_file), unit='B', unit_scale=True, desc="Transcribing") as pbar:
                result = self.current_asr_model(
                    audio_file,
                    return_timestamps=True,
                    chunk_length_s=30,
                    stride_length_s=[5, 5]
                )
                pbar.update(os.path.getsize(audio_file))
                
            return result
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def format_transcript(self, transcript):
        if not transcript:
            return ""
            
        if not transcript.get("segments"):
            return transcript.get("text", "")
        
        formatted_text = ""
        for segment in transcript['segments']:
            start_time = str(timedelta(seconds=int(segment['start'])))
            end_time = str(timedelta(seconds=int(segment['end'])))
            formatted_text += f"[{start_time} - {end_time}]\n{segment['text']}\n\n"
        return formatted_text.strip()

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                try:
                    os.remove(os.path.join(self.temp_dir, file))
                except Exception:
                    pass