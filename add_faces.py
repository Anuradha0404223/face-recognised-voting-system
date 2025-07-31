import tkinter as tk
from tkinter import messagebox
import cv2
import os
import pickle
import numpy as np
from PIL import Image, ImageTk
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
import pygame
import time

# ----------------------------- CONFIG -----------------------------
LANGUAGE = 'hi'  # default language: Hindi
MAX_FACES_PER_NUMBER = 3

# ----------------------------- SPEAK FUNCTION -----------------------------
def speak(text):
    tts = gTTS(text=text, lang=LANGUAGE)
    tts.save("temp.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    os.remove("temp.mp3")

# ----------------------------- TOGGLE LANGUAGE -----------------------------
def toggle_language():
    global LANGUAGE
    LANGUAGE = 'en' if LANGUAGE == 'hi' else 'hi'
    speak("भाषा बदली गई" if LANGUAGE == 'hi' else "Language switched")

# ----------------------------- FACE SIMILARITY -----------------------------
def is_duplicate_face(new_face, known_faces):
    if len(known_faces) == 0:
        return False
    similarities = cosine_similarity([new_face], known_faces)
    max_sim = np.max(similarities)
    return max_sim > 0.8

# ----------------------------- MAIN REGISTRATION FUNCTION -----------------------------
def register_face(name, mobile):
    if not name or not mobile:
        speak("कृपया नाम और मोबाइल नंबर भरें" if LANGUAGE == 'hi' else "Please enter name and mobile number")
        return

    if os.path.exists("voters.csv"):
        with open("voters.csv", "r") as f:
            lines = f.readlines()
            if any(mobile == line.strip().split(",")[1] for line in lines):
                count = sum(1 for line in lines if mobile == line.strip().split(",")[1])
                if count >= MAX_FACES_PER_NUMBER:
                    speak("एक मोबाइल नंबर से अधिकतम तीन पंजीकरण की अनुमति है" if LANGUAGE == 'hi' else "Maximum 3 registrations allowed per mobile number")
                    return

    cap = cv2.VideoCapture(0)
    speak("चेहरे को कैमरे के सामने रखें" if LANGUAGE == 'hi' else "Place your face in front of the camera")

    count = 0
    faces_data = []
    while count < 20:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for x, y, w, h in faces:
            face = gray[y:y + h, x:x + w]
            face = cv2.resize(face, (50, 50)).flatten()
            faces_data.append(face)
            count += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Registering Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not faces_data:
        speak("कोई चेहरा नहीं मिला" if LANGUAGE == 'hi' else "No face detected")
        return

    if os.path.exists("faces_data.pkl"):
        with open("faces_data.pkl", "rb") as f:
            known_faces = pickle.load(f)
    else:
        known_faces = []

    for face in faces_data:
        if is_duplicate_face(face, known_faces):
            speak("यह चेहरा पहले से मौजूद है" if LANGUAGE == 'hi' else "This face already exists")
            return

    known_faces.extend(faces_data)
    with open("faces_data.pkl", "wb") as f:
        pickle.dump(known_faces, f)

    if os.path.exists("names.pkl"):
        with open("names.pkl", "rb") as f:
            names = pickle.load(f)
    else:
        names = []

    names.extend([mobile] * len(faces_data))
    with open("names.pkl", "wb") as f:
        pickle.dump(names, f)

    with open("voters.csv", "a") as f:
        f.write(f"{name},{mobile}\n")

    speak("पंजीकरण सफल रहा" if LANGUAGE == 'hi' else "Registration successful")

# ----------------------------- GUI -----------------------------
root = tk.Tk()
root.title("Face Registration")
root.attributes('-fullscreen', True)

frame = tk.Frame(root)
frame.pack(pady=50)

tk.Label(frame, text="नाम / Name:", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10)
name_entry = tk.Entry(frame, font=("Arial", 16))
name_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame, text="मोबाइल नंबर / Mobile Number:", font=("Arial", 16)).grid(row=1, column=0, padx=10, pady=10)
mobile_entry = tk.Entry(frame, font=("Arial", 16))
mobile_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Button(root, text="📝 चेहरा पंजीकृत करें / Register Face", font=("Arial", 18), command=lambda: register_face(name_entry.get(), mobile_entry.get())).pack(pady=20)
tk.Button(root, text="🔁 भाषा बदलें / Switch Language", font=("Arial", 14), command=toggle_language).pack(pady=10)
tk.Button(root, text="❌ बंद करें / Exit", font=("Arial", 14), command=root.destroy).pack(pady=10)

root.mainloop()
