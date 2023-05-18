from flask import Flask, render_template, request, Response, url_for, redirect, flash
import sqlite3
import cv2
from ferg import fer
import webscrapper as ws
import re

# Initiating the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jok1234'
camera=cv2.VideoCapture(0)

# Creates connection to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Recommender page
@app.route('/recommender')
def recommender():
    return render_template('recommender.html')

# Saving image of the user
@app.route('/snap', methods=['POST'])
def snap():
    cv2.imwrite('snap.jpg', frame0)
    camera.release()
    cv2.destroyAllWindows()
    return redirect(url_for('results'))

# Initiating camera
def gen_frames():
    camera.open(0)
    while True:
        global frame, frame0
        success, frame = camera.read()
        frame=cv2.flip(frame,1)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame0=frame
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Display camera
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Camera page
@app.route('/live_feed')
def live_feed():
    return render_template('live_feed.html')

# Search page
@app.route('/word_search')
def word_search():
    return render_template('search.html')

# Search function
@app.route('/search', methods=['GET'])
def search():
    query=request.args.get('keyword')
    if query:
        conn=get_db_connection()
        ans=conn.execute('''SELECT artist, track FROM songs WHERE artist LIKE ? OR track LIKE ? LIMIT 10''', ("%"+query+"%", "%"+query+"%",)).fetchall()
        conn.close()
        if ans:
            return render_template('search_results.html', ans=ans)
        else:
            return redirect(url_for('word_search'), Response=flash("No results found! Try again", "danger"))
    return redirect(url_for('word_search'), Response=flash("Type something to search!", "warning"))

# Maps emotion to genres
def emotion_map(em):
    if em=="happy":
        return "hip_hop"
    elif em=="sad":
        return "country"
    elif em=="neutral":
        return "dance_pop"
    elif em=="angry":
        return "rock"
    else:
        return None

# Results function
@app.route('/results')
def results():
    results={}
    dominant_emotion=fer()
    genre=emotion_map(dominant_emotion)
    conn=get_db_connection()
    songs=conn.execute('''SELECT artist, track FROM songs WHERE genre = ? AND id in (SELECT id FROM SONGS ORDER BY RANDOM() LIMIT 30) LIMIT 10''', (genre,)).fetchall()
    results['emotion']=dominant_emotion
    results['songs']=songs
    conn.close()
    return render_template('results.html', results=results)

# Function to add songs to the database
@app.route('/add_song', methods=['GET'])
def add_song():
    artist=request.args.get('artist')
    track=request.args.get('song')
    conn=get_db_connection()
    exist=conn.execute('''SELECT artist, track FROM songs WHERE artist LIKE (?) AND track LIKE (?)''', (artist, track,)).fetchone()
    if not(exist):
        numbers_in_brackets_removed_artist = re.sub(r'\(.*\)',"",artist)
        numbers_in_brackets_removed_track = re.sub(r'\(.*\)',"",track)
        f_artist = re.sub(r'\W+', '', numbers_in_brackets_removed_artist).lower()
        f_track = re.sub(r'\W+', '', numbers_in_brackets_removed_track).lower()
        artist, track, lyrics=ws.fetch_lyrics(f_artist, f_track)
        if lyrics!="failed":
            genre=ws.predict_genre(lyrics)
            conn.execute('''
                        INSERT INTO songs (artist, track, genre, lyrics)
                        VALUES (?,?,?,?)
                        ''',
                        (artist, track, genre, lyrics)
                        )
            conn.commit()
            conn.close()
            return redirect(url_for('add'), Response=flash("Successfully added your song!", "success"))
        else:
            return redirect(url_for('add'), Response=flash("Failed! Try again.", "danger"))
    else:
        return redirect(url_for('add'), Response=flash("Song already added...", "info"))

# Add page
@app.route('/add')
def add():
    return render_template('add.html')

# main driver function
if __name__ == '__main__':
    app.run(debug=True)