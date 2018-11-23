#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
 
import speech_recognition as sr
from time import ctime
import time
import os
from gtts import gTTS
 
def speak(audioString):
    print(audioString)
    tts = gTTS(text=audioString, lang='pt')
    tts.save("audio.mp3")
    os.system("mpg321 audio.mp3")
 
def recordAudio():
    # Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
 
    # Speech recognition using Google Speech Recognition
    data = ""
    try:
        # Uses the default API key
        # To use another API key: `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        data = r.recognize_google(audio, language="pt-BR")
        print("You said: " + data)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return data
 
def jarvis(data):
    data = data.lower()
    if "tudo bem" in data:
        speak("Tudo ótimo, e contigo?")
    
    elif "oi" in data:
        speak("olá!")
 
    elif "onde está" in data:
        data = data.split(" ")
        location = data[2]
        speak(location + " fica aqui:")
        os.system("chromium-browser https://www.google.nl/maps/place/" + location + "/&amp;")
    else:
        speak("Desculpe, não entendi.")
 
# initialization
time.sleep(2)
speak("Olá, como posso ajudar?")
while 1:
    data = recordAudio()
    jarvis(data)