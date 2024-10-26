# Spotify Playlist Generator

## Overview
The **Spotify Playlist Generator** is an innovative application designed to curate personalized playlists based on user-inputted activities and moods. By leveraging sentiment analysis and machine learning, this project aims to enhance the listening experience, providing users with music that aligns with their emotional state and current activity.

## Features
- **Mood Classification**: Analyzes user input to classify mood into categories: happy, angry, sad, tired, anxious, and neutral.
- **Playlist Recommendation**: Fetches playlists from Spotify based on the user's mood and activity.
- **User Feedback**: Captures user feedback to refine and improve playlist recommendations over time.
- **Interactive GUI**: User-friendly interface built with Tkinter for seamless interaction.

## Purpose
This project aims to help users find the right music to accompany their activities and emotional states. Whether someone is working out, studying, or just feeling low, the Spotify Playlist Generator curates music that matches their mood, enhancing productivity and emotional well-being.

## How It Works
1. **User Input**: Users enter their current activity and mood.
2. **Mood Analysis**: The application uses sentiment analysis to classify the mood.
3. **Machine Learning**: 
   - The project employs a decision tree classifier trained on a dataset of user inputs and corresponding moods. This machine learning model helps predict the user's mood based on their activity description.
   - Ongoing efforts are aimed at refining the mood recognition process by experimenting with different algorithms and feature sets to enhance accuracy.
4. **Playlist Generation**: Based on the mood and activity, it queries Spotify's API to retrieve relevant playlists.
5. **Display Recommendations**: Recommendations are displayed in an interactive popup window, allowing users to access playlists directly.

## Technologies Used
- **Programming Languages**: 
  - Python
- **Libraries and Frameworks**:
  - **Spotipy**: For interacting with the Spotify API.
  - **NLTK (Natural Language Toolkit)**: For sentiment analysis using VADER.
  - **Pandas**: For data manipulation and storage of user feedback.
  - **Tkinter**: For creating the graphical user interface.
  - **Scikit-learn**: For implementing the decision tree classifier for mood prediction.
  - **PIL (Pillow)**: For image handling within the GUI.

## Future Improvements
**Enhanced Mood Detection**: Incorporate more advanced NLP techniques and explore deep learning models for better mood classification.
**Expanded Feedback Loop**: Implement a more sophisticated feedback mechanism to improve playlist recommendations.

## If you have suggestions for improvements feel free to reach out!

## Installation
To run this project locally, follow these steps:
1. Clone the repository:

   git clone https://github.com/SammyAbbas1/spotify-playlist-generator.git
   cd spotify-playlist-generator
   
2. Install the required libraries:
   
   pip install spotipy nltk pandas scikit-learn pillow
   
3. Obtain your Spotify API credentials by creating an app on the Spotify Developer Dashboard
   and replace the placeholder credentials in the code.

4. Run the application:

   python Spotify_PG.py
   
**Please let me know if you have any trouble running or accessing it**
