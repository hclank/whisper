import os
import soundfile as sf
import numpy as np
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqTranscriber:
    def __init__(self, sample_rate=16000):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.sample_rate = sample_rate
        self.temp_file = "temp_dictation.wav"

    def process(self, audio_data):
        if not audio_data:
            return ""

        audio_concat = np.concatenate(audio_data, axis=0)
        sf.write(self.temp_file, audio_concat, self.sample_rate)

        try:
            with open(self.temp_file, "rb") as file:
                raw_text = self.client.audio.transcriptions.create(
                    file=(self.temp_file, file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="text",
                )

            prompt = """
            Rewrite the raw speech transcript into clean, properly punctuated text. 
            Remove fillers (um, ah, like), fix self-corrections inline. 
            Output ONLY the polished text.
            """
            chat = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": raw_text},
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
            )
            return chat.choices[0].message.content
        finally:
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
