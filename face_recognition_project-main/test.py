from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle as pkl
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

# File paths
names_path = r'face_recognition_project-main\data\names.pkl'
faces_data_path = r'face_recognition_project-main\data\faces_data.pkl'
imgBg = r'face_recognition_project-main\groupbg.png'

# Create the Attendance directory if it doesn't exist
attendance_dir = 'Attendance'
if not os.path.exists(attendance_dir):
    os.makedirs(attendance_dir)

# Load the trained data
try:
    with open(names_path, 'rb') as w:
        LABELS = pkl.load(w)
    with open(faces_data_path, 'rb') as f:
        FACES = pkl.load(f)
except FileNotFoundError as e:
    print(f"File not found: {e.filename}")
    exit()
except OSError as e:
    print(f"OS error: {e}")
    exit()

print('Shape of Faces matrix --> ', FACES.shape)

# Initialize the KNN classifier
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Load the background image
imgBackground = cv2.imread(imgBg)
if imgBackground is None:
    print("Error: 'groupbg.png' not found or cannot be read.")
    exit()

# Initialize video capture
video = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

COL_NAMES = ['NAME', 'TIME', 'DATE', 'STATUS']

def check_clock_status(name, date):
    """Check if person has already clocked in/out today"""
    try:
        with open(f"Attendance/Attendance_{date}.csv", 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip header
            for row in csvreader:
                if row[0] == name:
                    return row[3]  # Return last status
    except:
        return None
    return None

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Could not read frame from video stream.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        
        # Check current status
        current_status = check_clock_status(str(output[0]), date)
        
        # Determine next status
        next_status = "CLOCK IN" if current_status is None or current_status == "CLOCK OUT" else "CLOCK OUT"
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, f"{str(output[0])} - {next_status}", (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
        
        attendance = [str(output[0]), str(timestamp), str(date), next_status]
    
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame", imgBackground)
    k = cv2.waitKey(1)
    
    if k == ord('o'):
        speak(f"Attendance Taken.. {next_status}")
        time.sleep(2)
        exist = os.path.isfile(f"Attendance/Attendance_{date}.csv")
        
        if exist:
            with open(f"Attendance/Attendance_{date}.csv", "+a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(attendance)
        else:
            with open(f"Attendance/Attendance_{date}.csv", "+a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(COL_NAMES)
                writer.writerow(attendance)
    
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
