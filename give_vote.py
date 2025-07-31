import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
import tempfile
import pygame
import time
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk
from deepface import DeepFace

# Language default
language_mode = 'hindi'

# Speak text using gTTS
def speak(text):
    try:
        lang = 'hi' if language_mode == 'hindi' else 'en'
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            temp_path = fp.name
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove(temp_path)
    except Exception as e:
        print("TTS Error:", e)

# Match face using DeepFace
def match_face_with_deepface(test_img_path):
    db_path = "data/registered_faces"
    if not os.path.exists(db_path) or not os.listdir(db_path):
        print("DeepFace Error: No item found in data/registered_faces")
        return None
    try:
        result = DeepFace.find(img_path=test_img_path, db_path=db_path, enforce_detection=False, model_name='Facenet')
        if len(result) > 0 and not result[0].empty:
            matched_file = result[0].iloc[0]["identity"]
            name = os.path.basename(matched_file).split("_")[0]
            return name
    except Exception as e:
        print("DeepFace Error:", e)
    return None

# Start camera and detect face
def start_face_detection():
    speak("कृपया कैमरे की ओर देखें।" if language_mode == 'hindi' else "Please look at the camera.")
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        speak("कैमरा चालू नहीं हो रहा है।" if language_mode == 'hindi' else "Unable to access the camera.")
        messagebox.showerror("Camera Error", "Camera not detected. Make sure it's connected and not used by another app.")
        return None

    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    captured_face_path = "temp_face.jpg"

    while True:
        ret, frame = video.read()
        if not ret:
            speak("कैमरे से वीडियो प्राप्त नहीं हो रहा है।" if language_mode == 'hindi' else "Failed to capture video.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            cv2.imwrite(captured_face_path, face_img)
            video.release()
            cv2.destroyAllWindows()
            return match_face_with_deepface(captured_face_path)

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()
    return None

# Record vote
def vote(party):
    global voter_name
    if not voter_name:
        speak("चेहरा मान्यता प्राप्त नहीं हुआ।" if language_mode == 'hindi' else "Face not recognized.")
        return

    df = pd.read_csv("Votes.csv") if os.path.exists("Votes.csv") else pd.DataFrame(columns=["NAME", "PARTY", "DATE", "TIME"])
    if voter_name in df["NAME"].values:
        speak("आप पहले ही मतदान कर चुके हैं।" if language_mode == 'hindi' else "You have already voted.")
        return

    now = datetime.now()
    df.loc[len(df)] = [voter_name, party, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")]
    df.to_csv("Votes.csv", index=False)

    speak(f"आपने {party} को वोट दिया। धन्यवाद!" if language_mode == 'hindi' else f"You have voted for {party}. Thank you!")
    messagebox.showinfo("Vote Recorded", f"Vote for {party} recorded successfully.")
    root.after(2000, root.quit)

# Toggle language
def toggle_language():
    global language_mode
    language_mode = 'english' if language_mode == 'hindi' else 'hindi'
    lang_btn.config(text="🇮🇳 हिंदी" if language_mode == 'english' else "🇬🇧 English")

# GUI setup
root = tk.Tk()
root.title("Face Voting System")
root.attributes("-fullscreen", True)

voter_name = start_face_detection()
if not voter_name:
    speak("चेहरा पहचान में नहीं आया।" if language_mode == 'hindi' else "Face not recognized.")
    messagebox.showerror("Face Not Recognized", "Voting aborted.")
    root.quit()
else:
    speak(f"{voter_name}, कृपया पार्टी चुनें।" if language_mode == 'hindi' else f"{voter_name}, please choose a party.")

parties = {
    "BJP": "bjp.png",
    "Congress": "congress.png",
    "AAP": "aap.png",
    "Others": "others.png"
}

frame = tk.Frame(root, bg="white")
frame.pack(pady=30)

row = 0
col = 0
for party, logo in parties.items():
    path = os.path.join("logos", logo)
    if os.path.exists(path):
        img_raw = Image.open(path).resize((150, 150))
        img = ImageTk.PhotoImage(img_raw)
        btn = tk.Button(frame, image=img, text=party, compound="top", font=("Arial", 16),
                        width=200, height=200, command=lambda p=party: vote(p))
        btn.image = img
        btn.grid(row=row, column=col, padx=30, pady=30)
    col += 1
    if col == 3:
        row += 1
        col = 0

lang_btn = tk.Button(root, text="🇮🇳 हिंदी" if language_mode == 'english' else "🇬🇧 English",
                     command=toggle_language, font=("Arial", 14))
lang_btn.pack(pady=10)

exit_btn = tk.Button(root, text="❌ Exit", command=root.quit, font=("Arial", 14), bg="red", fg="white")
exit_btn.pack(pady=10)

root.mainloop()
