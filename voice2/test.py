# voice_assistant.py - Fully Working Armenian Voice Assistant
# voice_assistant.py - Armenian Voice Assistant with Deepgram STT & TTS
import os
import tempfile
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from groq import Groq
from dotenv import load_dotenv
import time
import pygame
import requests
import json
import speech_recognition as sr
from gtts import gTTS
import speech_recognition as sr

load_dotenv()

class ArmenianVoiceBankAssistant:
    def __init__(self):
        # Initialize Groq
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.model = "llama-3.3-70b-versatile"
        
        # Audio settings
        self.sample_rate = 16000
        self.record_seconds = 5
        
        # System prompt in Armenian
        self.system_prompt = """Դուք Հայաստանի բանկային օգնական եք:

ԿԱՐԵՎՈՐ ԿԱՆՈՆՆԵՐ:
1. ՊԱՏԱՍԽԱՆԵԼ ՄԻԱՅՆ հետևյալ թեմաներով:
   - Վարկեր (սպառողական, հիփոթեք, ավտովարկ)
   - Ավանդներ (ժամկետային, ընթացիկ)
   - Մասնաճյուղերի հասցեներ և աշխատանքային ժամեր

2. ԵԹԵ հարցը ԱՅԼ ԹԵՄԱՅԻՑ Է, պատասխանել:
   "Ներողություն, ես կարող եմ օգնել միայն վարկերի, ավանդների և մասնաճյուղերի հարցերով:"

3. Պատասխանել հայերեն լեզվով:
4. Պատասխանները լինեն հակիրճ և օգտակար:"""
    
    def record_audio(self):
        """Record audio with volume meter"""
        print("\n🔴 Recording... (speak now for 5 seconds)")
        
        recording = sd.rec(
            int(self.record_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        
        # Show volume meter
        for i in range(50):
            time.sleep(0.1)
            if i < len(recording):
                current = recording[:i*320] if i*320 < len(recording) else recording
                if len(current) > 0:
                    mean_val = np.mean(current**2)
                    if mean_val > 0:
                        volume = np.sqrt(mean_val) * 1000
                        bar_length = min(40, int((volume / 5000) * 40))
                        bar = "█" * bar_length + "░" * (40 - bar_length)
                        print(f"\rVolume: [{bar}] {volume:>5.0f}", end="", flush=True)
        
        sd.wait()
        print("\n✅ Recording finished!")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        wav.write(temp_file.name, self.sample_rate, recording)
        
        return temp_file.name
    

    def speech_to_text(self, audio_file):
        """Convert Armenian speech to text using Google (free)"""
        try:
            print("📝 Transcribing Armenian speech...")
            
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            text = recognizer.recognize_google(audio, language="hy-AM")
            print(f"🎤 Recognized: {text}")
            return text
            
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
            return None
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return None
        
    

    def text_to_speech(self, text):
        """Convert text to speech using gTTS (free, supports Armenian)"""
        try:
            print("🔊 Generating Armenian speech...")
            
            tts = gTTS(text=text, lang='am', slow=False)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            
            print("✅ Speech generated")
            return temp_file.name
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None
    
    def play_audio(self, file_path):
        """Play audio file"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            print("✅ Playback finished")
        except Exception as e:
            print(f"❌ Playback error: {e}")
    
    def get_response(self, question):
        """Get text response from Groq"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Սխալ: {str(e)}"
    
    def run(self):
        """Main loop - FULL VOICE ASSISTANT"""
        print("=" * 60)
        print("🎤 Հայկական Ձայնային Բանկային Օգնական")
        print("🎯 FULL VOICE MODE - Speak in Armenian")
        print("=" * 60)
        print("\nԻնչպես օգտագործել:")
        print("1. Սեղմեք Enter")
        print("2. Խոսեք հայերեն (5 վայրկյան)")
        print("3. Սպասեք պատասխանին")
        print("4. Լսեք ձայնային պատասխանը")
        print("\nԴուրս գալու համար ասեք 'ելք' կամ Ctrl+C")
        print("=" * 60)
        
        while True:
            try:
                input("\n🎙️ Սեղմեք Enter և խոսեք...")
                
                # Record voice
                audio_file = self.record_audio()
                
                # Convert speech to text
                question = self.speech_to_text(audio_file)
                
                if not question:
                    print("⚠️ Չհասկացա, խնդրում եմ կրկնել:")
                    # Clean up and continue
                    try:
                        os.unlink(audio_file)
                    except:
                        pass
                    continue
                
                if question.lower() in ['ելք', 'exit', 'quit', 'bye']:
                    print("👋 Ցտեսություն!")
                    break
                
                # Get response from LLM
                print("\n🤔 Մտածում եմ...")
                answer = self.get_response(question)
                
                # Print response
                print(f"\n🤖 Օգնական: {answer}")
                
                # Convert to speech and play
                audio_output = self.text_to_speech(answer)
                if audio_output:
                    print("🔊 Խոսում եմ...")
                    self.play_audio(audio_output)
                    try:
                        os.unlink(audio_output)
                    except:
                        pass
                
                # Clean up
                try:
                    os.unlink(audio_file)
                except:
                    pass
                
                print("\n" + "-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Ցտեսություն!")
                break
            except Exception as e:
                print(f"❌ Սխալ: {e}")
                import traceback
                traceback.print_exc()

# Run the assistant
if __name__ == "__main__":
    print("\n🚀 Starting Armenian Voice Bank Assistant...\n")
    
    # Check for API keys
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in .env file")
        print("Add to .env: GROQ_API_KEY=your_key_here")
    elif not os.getenv("DEEPGRAM_API_KEY"):
        print("❌ DEEPGRAM_API_KEY not found in .env file")
        print("Add to .env: DEEPGRAM_API_KEY=your_key_here")
    else:
        assistant = ArmenianVoiceBankAssistant()
        assistant.run()