# Import necessary libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import tkinter as tk
from tkinter import messagebox, Text
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
import webbrowser
from PIL import Image, ImageTk

# Setting up API access
# Initialize Spotify client with credentials
sp = spotipy.Spotify(client_credentials_manager = SpotifyClientCredentials(client_id = "YOUR_SPOTIFY_CLIENT_ID", client_secret = "YOUR_SPOTIFY_CLIENT_SECRET"))

# Function to fetch playlists based on activity or mood
def get_playlists(query):
    try:
        # Search for playlists matching the query
        results = sp.search(q=query, type='playlist', limit=5)
        return results['playlists']['items']
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return []

# Function to analyze user mood using VADER sentiment analysis
def analyze_mood(user_input):
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(user_input)
    
    # Defining mood categories based on sentiment score
    compound = sentiment['compound']
    if compound >= 0.05:
        return 'happy'
    elif 0.1 <= compound < 0.5:
        return 'neutral'
    elif 0 <= compound < 0.1:
        return 'tired'
    elif -0.1 <= compound < 0:
        return 'anxious'
    elif -0.5 <= compound < -0.1:
        return 'sad'
    else:
        return 'angry'

# Machine Learning Model for Mood Classification
class MoodClassifier:
    def __init__(self):
        # Sample data for training the model
        self.data = [
            ("I'm feeling great!", "happy"),
            ("I feel like I am going to explode", "anger"),
            ("I feel so low today.", "sad"),
            ("I'm really exhausted.", "tired"),
            ("I'm indifferent about this.", "neutral"),
            ("I'm really worried", "anxious"),
        ]
        
        # Create features and labels for the model
        self.vectorizer = CountVectorizer()
        self.X = self.vectorizer.fit_transform([text for text, mood in self.data])
        self.y = [mood for text, mood in self.data]
        
        # Train the Decision Tree Classifier
        self.model = DecisionTreeClassifier()
        self.model.fit(self.X, self.y)
    
    # Predict mood based on user input
    def predict(self, user_input):
        input_vector = self.vectorizer.transform([user_input])
        return self.model.predict(input_vector)[0]

# Initialize the mood classifier
mood_classifier = MoodClassifier()

# Function to get user input from the GUI
def get_user_input():
    # Get activity and mood input from entry fields
    activity = activity_entry.get()
    mood_input = mood_entry.get()
    # Analyze mood using the input text
    mood = analyze_mood(mood_input)
    return activity, mood

# Function to recommend playlists based on activity and mood
def recommend_playlist(activity, mood):
    # Create a search query
    playlist_query = f"{activity} {mood} music"
    # Fetch playlists using the query
    playlists = get_playlists(playlist_query)
    
    if playlists:
        playlist_list = []
        for i, playlist in enumerate(playlists):
            # Format playlist information
            playlist_list.append(f"{i+1}. {playlist['name']} - {playlist['external_urls']['spotify']}")
        return "\n".join(playlist_list)
    else:
        return "No playlists found. Try different inputs."

# Function to create the feedback GUI window
def get_feedback_gui(activity, mood, playlist):
    feedback_window = tk.Toplevel()
    feedback_window.title("Playlist Feedback")
    feedback_window.geometry("400x300")
    
    # Prompt user for feedback
    prompt_label = tk.Label(feedback_window, text="Did you like the playlist?")
    prompt_label.pack(pady=(20, 10))
    
    # Frame for Yes and No buttons
    button_frame = tk.Frame(feedback_window)
    button_frame.pack(pady=(0, 10))
    
    feedback_type = tk.StringVar()
    # Buttons for Yes and No feedback
    yes_button = tk.Button(button_frame, text="Yes", command=lambda: feedback_type.set('yes'))
    yes_button.pack(side='left', padx=(0, 5))
    
    no_button = tk.Button(button_frame, text="No", command=lambda: feedback_type.set('no'))
    no_button.pack(side='left', padx=(5, 0))
    
    # Text field to collect additional comments (optional)
    comment_label = tk.Label(feedback_window, text="Additional comments:")
    comment_label.pack(pady=(10, 5))
    
    comment_entry = tk.Entry(feedback_window, width=40)
    comment_entry.pack(pady=(0, 10), padx=20, anchor='center')
    
    # Button for submitting feedback
    submit_button = tk.Button(
        feedback_window,
        text="Submit",
        command=lambda: submit_feedback_csv(
            feedback_type.get(),
            comment_entry.get(),
            activity,
            mood,
            playlist,
            feedback_window
        )
    )
    submit_button.pack(pady=(10, 20))

# Function to save feedback to a CSV file and close the feedback window
def submit_feedback_csv(feedback, comments, activity, mood, playlist, feedback_window):
    feedback_data = {
        'Activity': activity,
        'Mood': mood,
        'Playlist': playlist,
        'Feedback': feedback,
        'Comments': comments
    }
    try:
        # Read existing feedback data
        df = pd.read_csv('feedback.csv')
        new_data = pd.DataFrame([feedback_data])
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        # If no existing file, create a new one
        df = pd.DataFrame([feedback_data])
    
    # Save the updated feedback data
    df.to_csv('feedback.csv', index=False)
    # Close the feedback window
    feedback_window.destroy()

# Function to display playlist recommendations in a popup window
def show_popup(playlists, mood, main_window):
    # Create a new popup window
    popup = tk.Toplevel()
    popup.title("Playlist Recommendation")
    popup.geometry("400x320")
    
    # Load and display the Spotify logo
    image = Image.open("spotify_logo.jpg")
    image = image.resize((170, 70), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image)
    image_label = tk.Label(popup, image=tk_image)
    image_label.image = tk_image  # Keep a reference to prevent garbage collection
    image_label.pack(pady=10)
    
    # Display the detected mood and playlists
    message = f"Detected mood: {mood}\n\nPlaylists:"
    message_label = tk.Label(popup, text=message)
    message_label.pack(pady=(0, 2))
    
    # Frame for clickable playlist links
    top_frame = tk.Frame(popup)
    top_frame.pack(fill='both', padx=10)
    
    # Create clickable labels for each playlist
    for line in playlists.split("\n"):
        try:
            playlist_name, playlist_url = line.split(" - ")
            clickable_label = tk.Label(popup, text=playlist_name, fg="blue", cursor="hand2")
            clickable_label.pack(pady=(0, 2))
            clickable_label.bind("<Button-1>", lambda e, url=playlist_url: webbrowser.open(url))
        except ValueError:
            print("Playlist format error:", line)
    
    # Spacer frame to fill remaining space
    spacer_frame = tk.Frame(popup)
    spacer_frame.pack(expand=True, fill='both')
    
    # Function to close both popup and main window
    def close_both():
        popup.destroy()
        main_window.destroy()
    
    # Close button to exit the application
    close_button = tk.Button(popup, text="Close", command=close_both)
    close_button.pack(pady=10)

# Function to process user input and generate playlist recommendations
def submit():
    activity, mood = get_user_input()
    playlists = recommend_playlist(activity, mood)
    
    if playlists:
        show_popup(playlists, mood, root)
        first_playlist = playlists.split("\n")[0] if playlists else None
        if first_playlist:
            # Delay feedback GUI to allow user to view playlists
            root.after(2000, get_feedback_gui, activity, mood, playlists)
    else:
        messagebox.showwarning("Input Error", "Please describe how you're feeling.")

# Create the main application window
root = tk.Tk()
root.title("Spotify Playlist Generator")
root.geometry("400x300")  # Window size

# Frame for main content
root_frame = tk.Frame(root)
root_frame.pack(pady=10, fill='both', expand=True)

# Load and display the Spotify logo
image = Image.open("spotify_logo.jpg")
image = image.resize((170, 70), Image.LANCZOS)
tk_image = ImageTk.PhotoImage(image)
image_label = tk.Label(root_frame, image=tk_image)
image_label.image = tk_image
image_label.pack(pady=10)

# Frame for user input fields
input_frame = tk.Frame(root_frame)
input_frame.pack(pady=10)

# Activity input field
activity_label = tk.Label(input_frame, text="Activity (e.g. studying, working out, etc.)")
activity_label.pack(anchor='w', pady=(10, 5))
activity_entry = tk.Entry(input_frame)
activity_entry.pack(fill='x', padx=10, expand=True)

# Mood input field
mood_label = tk.Label(input_frame, text="Mood:")
mood_label.pack(anchor='w', pady=(10, 5))
mood_entry = tk.Entry(input_frame)
mood_entry.pack(fill='x', padx=10, expand=True)

# Submit button to generate playlist
submit_button = tk.Button(root_frame, text="Generate Playlist", command=submit)
submit_button.pack(pady=(20, 10), expand=True)

# Text widget for displaying output (optional, can be removed if unused)
output_text = Text(root_frame, height=10, width=50)
output_text.pack(pady=(10, 5))

# Start the GUI event loop
root.mainloop()