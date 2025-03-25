# Takes a video file, isolates who is talking, then generates a speech bubble with subtitles

# Input video file

# Generate text of what is being said

# Identify and isolate the location of people in shot
# - Give each person a unique lable to keep track of them between frames

# Determine who it talking
# - See if lips are moving
# - Speech recognition to identify who is talking if can't see lips
#   - Will have to see lips moving while talking (or being the only person in shot) to initially identify

# Make a speech bubble that tries not to overlap people

# Generate subtitles real time in the speech bubble

import cv2
import face_recognition
import numpy as np

DOWNSCALE_FACTOR = 4

cap = cv2.VideoCapture('res\moby_dick_5min.mp4')

while(cap.isOpened()):
    ret, frame = cap.read()
    frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
    small_frame = cv2.resize(frame, (0, 0), fx=1/DOWNSCALE_FACTOR, fy=1/DOWNSCALE_FACTOR)

    face_locations = face_recognition.face_locations(small_frame)
    face_landmarks_list = face_recognition.face_landmarks(small_frame)

    top = face_locations[0][0] * DOWNSCALE_FACTOR
    right = face_locations[0][1] * DOWNSCALE_FACTOR
    bottom = face_locations[0][2] * DOWNSCALE_FACTOR
    left = face_locations[0][3] * DOWNSCALE_FACTOR

    for face_landmarks in face_landmarks_list:
        for facial_feature in face_landmarks.keys():
            
            for index, item in enumerate(face_landmarks[facial_feature]): 
                if index == len(face_landmarks[facial_feature]) -1:
                    break
                cv2.line(frame, np.array(item)*DOWNSCALE_FACTOR, np.array(face_landmarks[facial_feature][index + 1])*DOWNSCALE_FACTOR, [0, 255, 0], 2) 

    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()