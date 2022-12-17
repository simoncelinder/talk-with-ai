import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS

# Cred to Tech With Tim for this code: https://www.youtube.com/watch?v=zqEoTxkh95M


def speak(text: str):
    tts = gTTS(text=text, lang='en')
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            # Google API for speech recognition
            said = r.recognize_google(audio)
        except Exception as e:
            print(f"Exception message: {e}")

    return said


speak("Hello")
#get_audio()
