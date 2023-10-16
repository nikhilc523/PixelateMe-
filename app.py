from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
import cv2
import os
import numpy as np
import random
import string
from flask import request, session, redirect, url_for
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask import session, redirect, url_for


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BLURRED_VIDEO_FOLDER'] = 'blurred_videos'
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Anitha7386@localhost:5432/pixelateme'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
# Define global variables
selected_faces = []
current_frame = None
window_name = 'Face Selection'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if request.form.get('action') == 'signup':
            email = request.form.get('email')

            try:
                # Create a new user
                new_user = User(username=username, password=password, email=email)
                db.session.add(new_user)
                db.session.commit()

                session['username'] = username
                return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                return 'Username or email already exists.'

        else:
            # Validate login credentials
            user = User.query.filter_by(username=username, password=password).first()
            if not user:
                return 'Invalid username or password.'

            session['username'] = username
            return redirect(url_for('index'))

    return render_template('login.html')



@app.route('/')
def index():
    if 'username' in session:
        user_name = get_current_user()
        return render_template('index.html', user_name=user_name)
    else:
        return redirect(url_for('login'))



@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/about')
def about():
    return render_template('about.html')
def get_downloaded_videos():
    downloaded_videos = []

    # Directory path where downloaded videos are stored
    download_directory = 'blurred_videos'

    # Iterate over the files in the download directory
    for filename in os.listdir(download_directory):
        if filename.endswith('.mp4'):
            video_path = os.path.join(download_directory, filename)
            video_size = os.path.getsize(video_path)
            video_info = {
                'filename': filename,
                'path': video_path,
                'size': video_size
            }
            downloaded_videos.append(video_info)

    return downloaded_videos

def get_current_user():
    if 'username' in session:
        return session['username']
    else:
        return None


@app.route('/download_history')
def download_history():
    downloaded_videos = get_downloaded_videos()
    return render_template('download_history.html', downloaded_videos=downloaded_videos)



@app.route('/process', methods=['POST'])
def process():
    if 'video' not in request.files:
        return 'No video file uploaded.', 400

    video = request.files['video']
    if video.filename == '':
        return 'No video file selected.', 400
    # Check video size
    video_size_mb = len(video.read()) / (1024 * 1024)  # Convert to MB
    video.seek(0)  # Reset the file pointer after reading the size

    if video_size_mb > 200:
        return 'Video size should be less than 200 MB.', 400

    # Save the video file to uploads folder
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(video_path)

    # Apply Gaussian blur to the video
    blurred_video_path = apply_blur(video_path, video)

    # Generate a random filename for the blurred video
    blurred_filename = generate_random_filename() + '.Mp4'
    blurred_video_path_renamed = os.path.join(app.config['BLURRED_VIDEO_FOLDER'], blurred_filename)
    os.rename(blurred_video_path, blurred_video_path_renamed)

    return redirect(url_for('result', filename=blurred_filename))
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()

    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename,mimetype='text/css')

@app.route('/blurred_videos/<path:filename>')
def download_blurred_video(filename):
    return send_from_directory(app.config['BLURRED_VIDEO_FOLDER'], filename, as_attachment=True)



def apply_blur(video_path, video):
    # Load video
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define output path for blurred video
    output_folder = app.config['BLURRED_VIDEO_FOLDER']
    os.makedirs(output_folder, exist_ok=True)
    blurred_video_path = os.path.join(output_folder, 'blurred_' + video.filename)

    # Create VideoWriter object to save the blurred video
    fourcc = cv2.VideoWriter_fourcc(*'Mp4v')
    out = cv2.VideoWriter(blurred_video_path, fourcc, fps, (width, height))

    # Perform face detection and apply blur
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Apply blur to the face region
            face_roi = frame[y:y + h, x:x + w]
            blurred_face = cv2.GaussianBlur(face_roi, (81, 81), 0)
            frame[y:y + h, x:x + w] = blurred_face

        # Write the frame to the output video
        out.write(frame)

    # Release resources
    cap.release()
    out.release()

    return blurred_video_path


def generate_random_filename():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(8))


if __name__ == '__main__':
    app.run(debug=True)

