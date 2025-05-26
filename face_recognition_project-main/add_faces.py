import cv2
import pickle
import numpy as np
import os
import time

# Define the correct data directory path for attendance
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Ensure the 'data' directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

video = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

faces_data = []
i = 0
start_time = time.time()
name = input("Enter Your Name: ")

print("Recording will start for 60 seconds. Please look at the camera.")

while True:
    ret, frame = video.read()
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(60 - int(elapsed_time), 0)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50))
        if len(faces_data) < 20 and i % 5 == 0:  # Capture every 5th frame until we have 20 samples
            faces_data.append(resized_img)
        i += 1
        cv2.putText(frame, f"Time left: {remaining_time}s", (30, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Samples: {len(faces_data)}/20", (30, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
    
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    
    # Exit if 'q' is pressed, 60 seconds have passed, or we have 20 samples
    if k == ord('q') or elapsed_time >= 60 or len(faces_data) >= 20:
        break

video.release()
cv2.destroyAllWindows()

# Ensure we have exactly 20 samples
if len(faces_data) >= 20:
    faces_data = faces_data[:20]  # Take only the first 20 samples
    faces_data = np.asarray(faces_data)
    faces_data = faces_data.reshape(20, -1)

    # Update the 'names.pkl' file in the attendance data folder
    names_path = os.path.join(DATA_DIR, 'names.pkl')
    if os.path.exists(names_path):
        with open(names_path, 'rb') as f:
            names = pickle.load(f)
        names = names + [name] * 20
    else:
        names = [name] * 20

    with open(names_path, 'wb') as f:
        pickle.dump(names, f)

    # Update the 'faces_data.pkl' file in the attendance data folder
    faces_data_path = os.path.join(DATA_DIR, 'faces_data.pkl')
    if os.path.exists(faces_data_path):
        with open(faces_data_path, 'rb') as f:
            faces = pickle.load(f)
        faces = np.append(faces, faces_data, axis=0)
    else:
        faces = faces_data

    with open(faces_data_path, 'wb') as f:
        pickle.dump(faces, f)

    print(f"Successfully added {name}'s data to the dataset with 20 samples.")
    print(f"Data saved in: {DATA_DIR}")
else:
    print("Not enough face samples collected. Please try again in better lighting conditions.")