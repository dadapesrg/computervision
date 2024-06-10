# Main libraries that are used
from functools import wraps
import datetime
import psutil
import platform
import yaml
import cv2

from ultralytics import YOLO
import os
from flask import (Flask, Response, redirect, url_for, jsonify, request, flash, render_template, session)
from flask_socketio import SocketIO, emit
import requests
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from picamera2 import Picamera2, MappedArray

# important to use the REST API BY GOOGLE
Firebase_api_key = 'AIzaSyCEL8kSwSyX4eIk6SeCQMtPGwCyzApvM2c'

# authenticate flask
app = Flask(__name__)
socketio = SocketIO(app)
# this is important to register users
app.secret_key = 'ILIKEEGGS'

# Using REST API by google to set up user Login and registration
FIREBASE_SIGN_UP = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={Firebase_api_key}'
FIREBASE_SIGN_in = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={Firebase_api_key}'

# Setting up protection function for routes
# Only registered users can have access to the database collection logs and Live feed
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_token' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# redirects you to the main feed on startup
@app.route('/')
@login_required
def home():
    return render_template('index.html')

# HTML page for the main video feed dashboard
@app.route('/Video_page')
@login_required
def video_page():
    return render_template('Video.html')

# redundant but just shows the camera feed without any dashboard/ui
@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Gets all the information from the fire base site in JSON format don't know if their another way will look into making it into a tabular form
@app.route('/data')
@login_required
def data():
    try:
        data = db_ref.get()
        return render_template('data.html', data=data)
    except Exception as e:
        return jsonify({"error": str(e)})

# For user creation on firebase
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # create new user r
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        try:
            response = requests.post(FIREBASE_SIGN_UP, json=payload)
            response_data = response.json()
            print(response_data)

            if 'idToken' in response_data:
                flash('user registered')
                return redirect(url_for('login'))
            else:
                error_message = response_data.get('error', {}).get('message', 'Unknown error')
                flash(f"Error creating user: {error_message}")
        except Exception as e:
            flash(f"error creating user :{str(e)}")
    return render_template('Register.html')

# For user login using firebase api key
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Authenticate with Firebase
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        try:
            response = requests.post(FIREBASE_SIGN_in, json=payload)
            response_data = response.json()
            print(response_data)

            if 'idToken' in response_data:
                session['id_token'] = response_data['idToken']
                flash('login worked yh')
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error=response_data.get('error', {}).get('message', 'Unknown error'))
        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('Login.html')

# terminate current user session
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('you have logged out')
    return redirect(url_for('login'))

# set firebase credentials
# they are in the project directory
cred = credentials.Certificate("Credentials.json")

# Live firebase database link
firebase_admin.initialize_app(cred, {"databaseURL": "https://alarm-notification-94a3c-default-rtdb.firebaseio.com/"})

# Initialize data reference
db_ref = db.reference()






# Load the labels from the config file in the directory
with open('config.yaml', 'r') as file:
    class_labels = yaml.safe_load(file)

# specify Labels and print them on the terminal for verification
LABELS = [class_labels['names'][i] for i in range(len(class_labels['names']))]
print(LABELS)

# set list of colours to represent the class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

# file directory to the trained model
model_path = "/home/admin/Desktop/project2/runs/detect/train62/weights/last.pt"
# Load a model
try:
    model = YOLO(model_path)
    print("MODEL LOADED")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()



# Threshold score determines whether the desired object detected is similar to the one in the model
threshold = 0.7

## Main Loop function
def generate_frames():
    #initizalte picam2
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    while True:
        frame = picam2.capture_array()
        frame=cv2.resize(frame,(320,240))#resize image
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)  # Convert the frame to RGB
        h, w, _ = frame.shape
        results = model(frame)[0]

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            x_min = int(max(0, x1))
            y_min = int(max(0, y1))
            x_max = int(min(h, x2))
            y_max = int(min(w, y2))

            if score > threshold:
                socketio.emit('object_detected', {'message': "WEAPON DETECTED!"})
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 4)
                cv2.putText(frame, results.names[int(class_id)].upper(), (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

                timestamp = datetime.datetime.now().isoformat()
                device_info = {
                    "OS": platform.system(),
                    "Version": platform.version(),
                    "processor": platform.processor(),
                    "Machine architecture": platform.machine()
                }
                data = {
                    "object": results.names[int(class_id)].upper(),
                    "timestamp": timestamp,
                    "Location": "Nigeria",
                    "Device": device_info
                }

                try:
                    db_ref.push(data)
                    print("Data pushed successfully!")
                except Exception as e:
                    print(f"Error pushing data to database: {e}")

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
