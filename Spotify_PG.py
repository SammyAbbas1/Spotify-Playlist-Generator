#Libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import tkinter as tk
from tkinter import messagebox, Text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from tkinter import PhotoImage
import webbrowser
from PIL import Image, ImageTk

#Setting up API access

#My credentials
sp = spotipy.Spotify(client_credentials_manager = SpotifyClientCredentials(client_id = "dda6968b1ed14ab89559df9e5e4cc3e5", client_secret = "d97348c3b59d4be3a6604702f2e88929"))

# Fetch Playlists based on activity or mood
def get_playlists(query):
    results = sp.search(q=query, type='playlist', limit=5)
    return results ['playlists']['items']

#Using Vader for mood classification
def analyze_mood(user_input):
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(user_input)

    #Defining mood categories
    if sentiment['compound'] >= 0.05:
        return 'happy'
    elif sentiment['compound'] >= 0.1:
        return 'angry'
    elif sentiment['compound'] <= -0.05 and sentiment['compound'] > -0.1:
        return 'anxious'
    elif sentiment['compound'] <= -0.1:
        return 'sad'
    elif sentiment['compound'] < 0.05 and sentiment['compound'] > -0.05:
        return 'tired'
    else:
        return 'neutral'

#ML Model for Mood Classification
class MoodClassifier:
    def __init__(self):
        #Sample data
        self.data = [
            ("I'm feeling great!", "happy"),
            ("I feel like I am going to explode", "anger"),
            ("I feel so low today.", "sad"),
            ("I'm really exhausted.", "tired"),
            ("I'm indifferent about this.", "neutral"),
            ("I'm really worried", "anxious"),
        ]

        #Create features and labels
        self.vectorizer = CountVectorizer()
        self.X = self.vectorizer.fit_transform([text for text, mood in self.data])
        self.y = [mood for text, mood in self.data]

        #Train model
        self.model = DecisionTreeClassifier()
        self.model.fit(self.X, self.y)

    def predict(self, user_input):
        input_vector = self.vectorizer.transform([user_input])
        return self.model.predict(input_vector)[0]

mood_classifier = MoodClassifier()

#User Input Interface   
def get_user_input():
    activity = activity_entry.get()
    mood_input = mood_entry.get()
    mood = analyze_mood(mood_input)
    return activity, mood

#Fetch and recommend a playlist based on activity and mood
def recommend_playlist(activity, mood):
    #print(f"Detected mood: {mood}")
    playlist_query = f"{activity} {mood} music"
    playlists = get_playlists(playlist_query)

    if playlists is not None:
        playlist_list = []
        for i, playlist in enumerate(playlists):
            playlist_list.append(f"{i+1}. {playlist['name']} - {playlist['external_urls']['spotify']}")
        
        return "\n".join(playlist_list)

    else:
        return "No playlists found. Try different inputs."


 #Capture feedback - for refining recommendation system    
def get_feedback(activity, mood, playlist):
    feedback = input("Did you like the playlist? (yes/no): ").lower()
    feedback_data = {'Activity': activity, 'Mood': mood, 'Playlist: ': playlist, 'Feedback': feedback}

    try:
        df = pd.read_csv('feedback.csv')
        #feedback_row = pd.DataFrame([feedback_data])
        new_data = pd.DataFrame([feedback_data])
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([feedback_data])

    df.to_csv('feedback.csv', index=False)


#Popup
def show_popup(playlists, mood, main_window):
    #New window
    popup = tk.Toplevel()
    popup.title("Playlist Recommendation")
    popup.geometry("400x320")

    #Resize and load the image
    image = Image.open("spotify_logo.jpg")
    image = image.resize((170, 70), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)

    #Label to hold image
    image_label = tk.Label(popup, image=tk_image)
    image_label.image = tk_image #reference to avoid garbage collection
    image_label.pack(pady=10)

    #Message and other elements for popup
    message = f"Detected mood: {mood}\n\nPlaylists:"
    message_label = tk.Label(popup, text=message)
    message_label.pack(pady=(0,2)) #set bottom padding to 5 to reduce space below label

    #Frame for logo and message
    top_frame = tk.Frame(popup)
    top_frame.pack(fill='both', padx=10)

    #Clickable playlist links
    for line in playlists.split("\n"):
        try: 
            playlist_name, playlist_url = line.split(" - ")
            clickable_label = tk.Label(popup, text=playlist_name, fg="blue", cursor="hand2")
            clickable_label.pack(pady=(0,2)) #set bottom padding to 2 for space between items
            clickable_label.bind("<Button-1>", lambda e, url=playlist_url: webbrowser.open(url))
        except ValueError:
            print("Playlist format error:", line)

    #Spacer frame to take up remaining
    spacer_frame = tk.Frame(popup)
    spacer_frame.pack(expand=True, fill='both')

    #Frame to keep close button at bottom
    #button_frame = tk.Frame(popup)
    #button_frame.pack(pady=(10,10), side='bottom')

    #Close popup
#    close_button = tk.Button(popup, text="Close", command=popup.destroy)
#    close_button.pack(pady=10)
    def close_both():
        popup.destroy()
        main_window.destroy()

    close_button = tk.Button(popup, text="Close", command=close_both)
    close_button.pack(pady=10)

#Function to process input
def submit():
    activity, mood = get_user_input()
    playlists = recommend_playlist(activity, mood)

    if playlists:
        show_popup(playlists, mood, root)
        #messagebox.showinfo("Generated Playlists", f"Detected mood: {mood}\n\nPlaylists:\n{playlists}")
        first_playlist = playlists.split("\n")[0] if playlists else None
        if first_playlist:
            get_feedback(activity, mood, first_playlist)

    else:
        messagebox.showwarning("Input Error", "Please describe how you're feeling.")


#Create main window
root = tk.Tk()
root.title("Dynamic Playlist Generator")
root.geometry("400x300") #Window size

#Frame
root_frame = tk.Frame(root)
root_frame.pack(pady=10, fill='both', expand=True)

#Load Pand resize image for main window
image = Image.open("spotify_logo.jpg")
image = image.resize((170, 70), Image.LANCZOS)
tk_image = ImageTk.PhotoImage(image)

#Label to display image in main window
image_label = tk.Label(root_frame, image=tk_image)
image_label.image = tk_image
image_label.pack(pady=10)

#Frame for user inputs
input_frame = tk.Frame(root_frame)
#input_frame.pack(pady=10, padx=10)
input_frame.pack(pady=10)

#Input fields
activity_label = tk.Label(input_frame, text="Activity (e.g. studying, working out, etc.)")
activity_label.pack(anchor='w', pady=(10,5)) #Align to the eft, add top padding
activity_entry = tk.Entry(input_frame)
activity_entry.pack(fill='x', padx=10, expand=True) #fill width and expand vertically

mood_label = tk.Label(input_frame, text="Mood:")
mood_label.pack(anchor='w', pady=(10,5)) #Align to the left, add top padding
mood_entry = tk.Entry(input_frame)
mood_entry.pack(fill='x', padx=10, expand=True)

#Submit button
submit_button = tk.Button(root_frame, text="Generate Playlist", command=submit)
submit_button.pack(pady=(20,10), expand=True)
#submit_button.pack(pady=10)

#Text widget for displaying output
output_text = Text(root_frame, height=10, width=50)
output_text.pack(pady=(10,5))

#Start GUI event loop
root.mainloop()