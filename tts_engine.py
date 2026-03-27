import re
from gtts import gTTS
from pydub import AudioSegment
import os
import tempfile

class TTSEngine:
    def __init__(self, output_dir="static/audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def change_speed(self, sound, speed=1.0):
        if speed == 1.0:
            return sound
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        })
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    def shift_pitch(self, sound, semitones):
        if semitones == 0:
            return sound
        new_sample_rate = int(sound.frame_rate * (2.0 ** (semitones / 12.0)))
        pitched = sound._spawn(sound.raw_data, overrides={"frame_rate": new_sample_rate})
        return pitched.set_frame_rate(sound.frame_rate)

    def generate_audio(self, text, emotion, confidence, speed, volume, pitch, pause_ms, filename="output.mp3"):
        # 1. Scale parameters dynamically by confidence score
        scaled_speed = 1.0 + (speed - 1.0) * confidence
        scaled_db = volume * confidence
        scaled_pitch = pitch * confidence
        
        silence_segment = AudioSegment.silent(duration=pause_ms)
        final_audio = AudioSegment.empty()
        
        # 2. Add specific intro silences
        if emotion in ["joy", "surprise"]:
            final_audio += AudioSegment.silent(duration=100)
        elif emotion == "sadness":
            final_audio += AudioSegment.silent(duration=300)
            
        # 3. Split input text into sentences using regex
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s for s in sentences if s]
        
        if not sentences:
            sentences = [text.strip()]
            
        # 4. Generate gTTS for each sentence and concatenate with appropriate pauses
        for i, sentence in enumerate(sentences):
            tts = gTTS(text=sentence, lang='en', slow=False)
            
            # Using tempfile to bridge gTTS output format to pydub ingestion
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            tts.save(temp_path)
            
            segment = AudioSegment.from_mp3(temp_path)
            final_audio += segment
            
            # Add silence between sentences except after the last one
            if i < len(sentences) - 1:
                final_audio += silence_segment
                
            os.remove(temp_path)
            
        # 5. Apply speed, volume, and pitch modulation to the ENTIRE concatenated audio
        final_audio = final_audio + scaled_db
        final_audio = self.shift_pitch(final_audio, scaled_pitch)
        final_audio = self.change_speed(final_audio, scaled_speed)
        
        # 6. Export the final mix
        output_path = os.path.join(self.output_dir, filename)
        final_audio.export(output_path, format="mp3")
        
        return output_path
