from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, session as login_session
from flask import render_template
from googleapiclient.discovery import build
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

app.secret_key = 'secret_key'

# Database connection
conn = sqlite3.connect('users.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS users
             (email TEXT PRIMARY KEY, password TEXT)''')

# Register view
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if user with the same email already exists
        cursor = conn.execute("SELECT email FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            error = "User with this email already exists"
            return render_template('register.html', error=error)
        else:
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
            return redirect('/login')
    else:
        return render_template('register.html')

# Login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user with the given email exists
        cursor = conn.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            # Check if the password is correct
            hashed_password = row[0]
            if check_password_hash(hashed_password, password):
                session['email'] = email
                return redirect('/')
        error = "Invalid email or password"
        # return render_template('login.html', error=error)
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# Logout view
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

# Homepage view (protected by login)
@app.route('/')
def home():
    if 'email' in session:
        # return "Welcome, " + session['email'] + "!"
        return render_template('homepage.html')
    else:
        return redirect('/login')



# #register page
# @app.route('/register')
# def register():
#     return render_template('register.html')

# #login page
# @app.route('/login')
# def login():
#     return render_template('login.html')

#about page
@app.route('/about')
def about():
    return render_template('about.html')

#contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# #media page
# @app.route('/media')
# def media():
#     return render_template('media.html')


# Replace with your own API key
YOUTUBE_API_KEY = 'AIzaSyBDnBWssZvy7lZyWbMnK3lY0whJJPoZ-WQ'

# Replace with your own channel ID
# YOUTUBE_CHANNEL_ID = 'Mejja official'

# Create a function to fetch the video data from the YouTube API
def get_youtube_videos():
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part='snippet',
        # channelId=YOUTUBE_CHANNEL_ID,
        maxResults=5,
        order='date'
    )
    response = request.execute()
    videos = []
    for item in response['items']:
        video = {
            'title': item['snippet']['title'],
            'video_id': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
        }
        videos.append(video)
    return videos

# Define a Flask route to render the media page
@app.route('/media')
def media():
    videos = get_youtube_videos()
    return render_template('media.html', videos=videos)



#run the app
if __name__ == '__main__':
    app.run(debug=True)