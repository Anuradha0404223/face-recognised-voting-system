import pandas as pd
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageTk
import os

# CSV file
CSV_FILE = "Votes.csv"
VOTER_FILE = "voters.csv"

# Theme and Language settings
current_theme = "light"
current_language = "english"

# Language Labels
labels = {
    "english": {
        "title": "Live Voting Dashboard",
        "name": "NAME",
        "party": "PARTY",
        "date": "DATE",
        "time": "TIME",
        "votes": "Votes",
        "vote_count": "Vote Count by Party",
        "refresh": "🔄 Refresh",
        "theme": "🌓 Toggle Theme",
        "language": "🈯 Toggle Language"
    },
    "hindi": {
        "title": "लाइव वोटिंग डैशबोर्ड",
        "name": "नाम",
        "party": "पार्टी",
        "date": "तारीख",
        "time": "समय",
        "votes": "वोट",
        "vote_count": "पार्टी के अनुसार वोटों की संख्या",
        "refresh": "🔄 ताज़ा करें",
        "theme": "🌓 थीम बदलें",
        "language": "🈯 भाषा बदलें"
    }
}

# Theme styles
themes = {
    "light": {
        "bg": "white",
        "fg": "black",
        "table_bg": "white",
        "bar_colors": ['orange', 'blue', 'green', 'red']
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "white",
        "table_bg": "#3c3f41",
        "bar_colors": ['#f39c12', '#3498db', '#2ecc71', '#e74c3c']
    }
}

# Load vote data
def load_data():
    if not os.path.exists(CSV_FILE):
        messagebox.showerror("Error", f"{CSV_FILE} not found.")
        return pd.DataFrame(columns=["NAME", "PARTY", "DATE", "TIME"])

    df = pd.read_csv(CSV_FILE)
    if "VOTE" in df.columns and "PARTY" not in df.columns:
        df.rename(columns={"VOTE": "PARTY"}, inplace=True)

    if os.path.exists(VOTER_FILE):
        try:
            voter_df = pd.read_csv(VOTER_FILE)
            df = df.merge(voter_df, left_on="NAME", right_on="MOBILE", how="left")
            df["NAME"] = df["NAME_y"].combine_first(df["NAME_x"])
            df = df[["NAME", "PARTY", "DATE", "TIME"]]
        except:
            pass

    return df

# Refresh table and plot
def refresh_table():
    df = load_data()
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.iterrows():
        tree.insert("", END, values=list(row))
    plot_votes(df)

# Plot bar chart
def plot_votes(df):
    ax.clear()
    vote_counts = df["PARTY"].value_counts()
    bars = ax.bar(vote_counts.index, vote_counts.values, color=themes[current_theme]['bar_colors'])

    ax.set_facecolor(themes[current_theme]['bg'])
    fig.patch.set_facecolor(themes[current_theme]['bg'])
    ax.set_title(labels[current_language]['vote_count'], color=themes[current_theme]['fg'], fontsize=14)
    ax.set_ylabel(labels[current_language]['votes'], color=themes[current_theme]['fg'])
    ax.set_xlabel(labels[current_language]['party'], color=themes[current_theme]['fg'])
    ax.tick_params(axis='x', colors=themes[current_theme]['fg'])
    ax.tick_params(axis='y', colors=themes[current_theme]['fg'])

    for bar, label in zip(bars, vote_counts.index):
        height = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2

        ax.text(x, height + 0.3, int(height), ha='center', color=themes[current_theme]['fg'], fontsize=10)

        logo_path = f"logos/{label.lower()}.png"
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((20, 20))
                imagebox = OffsetImage(img, zoom=1)
                ab = AnnotationBbox(imagebox, (x, height + 1.0), frameon=False)
                ax.add_artist(ab)
            except Exception as e:
                print(f"Error loading logo {logo_path}: {e}")

    canvas.draw()

# Toggle theme
def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()
    refresh_table()

# Toggle language
def toggle_language():
    global current_language
    current_language = "hindi" if current_language == "english" else "english"
    update_labels()
    refresh_table()

# Apply UI theme
def apply_theme():
    root.configure(bg=themes[current_theme]['bg'])
    title_label.configure(bg=themes[current_theme]['bg'], fg=themes[current_theme]['fg'])
    refresh_btn.configure(bg="#4CAF50", fg="white")
    theme_btn.configure(bg="#007ACC", fg="white")
    lang_btn.configure(bg="#ff9800", fg="white")
    style.theme_use("clam")
    style.configure("Treeview",
        background=themes[current_theme]['table_bg'],
        foreground=themes[current_theme]['fg'],
        fieldbackground=themes[current_theme]['table_bg'],
        rowheight=25,
        font=("Arial", 10))
    style.configure("Treeview.Heading",
        background="#f0f0f0",
        foreground="black" if current_theme == "light" else "white",
        font=("Arial", 10, "bold"))
    canvas.get_tk_widget().configure(bg=themes[current_theme]['bg'])

# Update text based on language
def update_labels():
    title_label.config(text=labels[current_language]['title'])
    for i, col in enumerate(["name", "party", "date", "time"]):
        tree.heading(columns[i], text=labels[current_language][col])
    refresh_btn.config(text=labels[current_language]['refresh'])
    theme_btn.config(text=labels[current_language]['theme'])
    lang_btn.config(text=labels[current_language]['language'])

# GUI Setup
root = Tk()
root.title("🗳️ Voting Dashboard")
root.geometry("850x600")

columns = ("NAME", "PARTY", "DATE", "TIME")
style = ttk.Style()

# Title
title_label = Label(root, text=labels[current_language]['title'], font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Table
frame = Frame(root)
frame.pack(pady=10)
tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(side=LEFT)
scrollbar = Scrollbar(frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=RIGHT, fill=Y)
tree.configure(yscrollcommand=scrollbar.set)

# Chart
fig = Figure(figsize=(6, 3.5), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Buttons
button_frame = Frame(root)
button_frame.pack(pady=10)
refresh_btn = Button(button_frame, text=labels[current_language]['refresh'], font=("Arial", 12), command=refresh_table)
refresh_btn.grid(row=0, column=0, padx=10)
theme_btn = Button(button_frame, text=labels[current_language]['theme'], font=("Arial", 12), command=toggle_theme)
theme_btn.grid(row=0, column=1, padx=10)
lang_btn = Button(button_frame, text=labels[current_language]['language'], font=("Arial", 12), command=toggle_language)
lang_btn.grid(row=0, column=2, padx=10)

# Start
apply_theme()
update_labels()
refresh_table()
root.mainloop()