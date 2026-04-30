#!/usr/bin/env python3
import cv2
import numpy as np
import subprocess
import json

input_video = "/home/esotericwarfare/Studying Vim Shortcuts Won't Make You a Good Programmer - George Hotz [9LJ2KrVZ1YI].mkv"
output_video = "/home/esotericwarfare/reel_vertical.mp4"

cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Load face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Output is 9:16 vertical (1080x1920)
out_width = 1080
out_height = 1920

# Calculate crop width to maintain aspect ratio for vertical video
# We want to crop a portion of the width to make it vertical
crop_width = int(height * 9 / 16)  # Width for 9:16 from original height
crop_width = min(crop_width, width)  # Don't exceed original width

# Track face positions
face_positions = []
frame_idx = 0

print(f"Analyzing video: {width}x{height}, {fps} fps, {total_frames} frames")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        # Get the largest face
        areas = [w * h for (x, y, w, h) in faces]
        largest_idx = np.argmax(areas)
        x, y, w, h = faces[largest_idx]
        center_x = x + w // 2
        face_positions.append(center_x)
    else:
        # Use last known position or center
        if face_positions:
            face_positions.append(face_positions[-1])
        else:
            face_positions.append(width // 2)
    
    frame_idx += 1
    if frame_idx % 100 == 0:
        print(f"Processed {frame_idx}/{total_frames} frames")

cap.release()

# Smooth face positions
smoothed = []
window = 30
for i in range(len(face_positions)):
    start = max(0, i - window // 2)
    end = min(len(face_positions), i + window // 2 + 1)
    smoothed.append(int(np.mean(face_positions[start:end])))

# Generate crop filter for ffmpeg
crop_filter = []
for i, cx in enumerate(smoothed):
    # Calculate crop x position (center the crop on the face)
    cx = max(crop_width // 2, min(width - crop_width // 2, cx))
    crop_x = cx - crop_width // 2
    crop_filter.append(f"{crop_x}")

# Write crop data to file
with open('/tmp/crop_positions.txt', 'w') as f:
    for pos in smoothed:
        cx = max(crop_width // 2, min(width - crop_width // 2, pos))
        f.write(f"{cx}\n")

print("Face tracking complete. Creating vertical video...")

# Use ffmpeg with zoompan to create vertical video
# We'll use a different approach: create a video with centered face cropping
filter_complex = f"""
[0:v]crop=w={crop_width}:h={height}:x='x':y=0,
scale={out_width}:{out_height}[v]
""".strip()

# Actually, let's use a simpler approach with a Python script that writes frames
print("Creating vertical video with face tracking...")

# Re-read video and create output
cap = cv2.VideoCapture(input_video)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (out_width, out_height))

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cx = smoothed[frame_idx]
    crop_x = max(0, min(width - crop_width, cx - crop_width // 2))
    
    # Crop the frame
    cropped = frame[:, crop_x:crop_x + crop_width]
    
    # Resize to output size
    resized = cv2.resize(cropped, (out_width, out_height))
    
    out.write(resized)
    
    frame_idx += 1
    if frame_idx % 100 == 0:
        print(f"Writing frame {frame_idx}/{total_frames}")

cap.release()
out.release()

print(f"Vertical video created: {output_video}")
