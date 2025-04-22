import streamlit as st
import pandas as pd
import time
from datetime import datetime
from PIL import Image
import os

# Timestamp and date
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# Autorefresh
from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")

# Display the counter
if count == 0:
    st.write("Count is zero")
elif count % 3 == 0 and count % 5 == 0:
    st.write("FizzBuzz")
elif count % 3 == 0:
    st.write("Fizz")
elif count % 5 == 0:
    st.write("Buzz")
else:
    st.write(f"Count: {count}")

# Upload image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    # Save uploaded image
    image_path = os.path.join("uploads", f"uploaded_image_{timestamp}.png")
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    image.save(image_path)

    st.write(f"Image saved at {image_path}")

    # Process the image for attendance (Placeholder for actual processing)
    # Add your face recognition and attendance logic here

# Read and display the attendance CSV file
attendance_file_path = f"Attendance/Attendance_{date}.csv"
if os.path.exists(attendance_file_path):
    df = pd.read_csv(attendance_file_path)
    st.dataframe(df.style.highlight_max(axis=0))
else:
    st.write("No attendance record found for today.")
