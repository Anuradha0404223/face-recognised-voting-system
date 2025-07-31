import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for i, voice in enumerate(voices):
    print(f"{i}: {voice.name} - {voice.id}")

engine.setProperty('voice', voices[0].id)  # Try another index if needed
engine.say("Hello, this is a test.")
engine.runAndWait()
