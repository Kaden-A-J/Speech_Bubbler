import face_recognition
import numpy as np
import cv2


DOWNSCALE_FACTOR = 8
FACE_TRACKING_RESET_RATE = 5


class face_tracker:
    def __init__(self):
        self.previous_face_points = [(0, 0)]
        self.previous_face_box = [(0, 0), (0, 0)]
        self.face_landmarks_list = None
        self.face_locations = None

    def project_face_tracking(self, frame, frame_no, features=True, box=True):
        small_frame = None

        if features:

            if frame_no % FACE_TRACKING_RESET_RATE == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=1/DOWNSCALE_FACTOR, fy=1/DOWNSCALE_FACTOR)
                self.face_landmarks_list = face_recognition.face_landmarks(small_frame)

            for face_landmarks in self.face_landmarks_list:
                for facial_feature in face_landmarks.keys():
                    
                    for index, item in enumerate(face_landmarks[facial_feature]): 
                        if index == len(face_landmarks[facial_feature]) -1:
                            break
                        cv2.line(frame, np.array(item)*DOWNSCALE_FACTOR, np.array(face_landmarks[facial_feature][index + 1])*DOWNSCALE_FACTOR, [0, 255, 0], 2) 
        
        face_points = []
        face_box = None
        if box:

            if frame_no % FACE_TRACKING_RESET_RATE == 0:
                if not small_frame:
                    small_frame = cv2.resize(frame, (0, 0), fx=1/DOWNSCALE_FACTOR, fy=1/DOWNSCALE_FACTOR)
                self.face_locations = face_recognition.face_locations(small_frame)

            if self.face_locations:
                top = self.face_locations[0][0] * DOWNSCALE_FACTOR
                right = self.face_locations[0][1] * DOWNSCALE_FACTOR
                bottom = self.face_locations[0][2] * DOWNSCALE_FACTOR
                left = self.face_locations[0][3] * DOWNSCALE_FACTOR
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                face_points.append(((right + left) / 2, (top + bottom) / 2))
                face_box = [(top, left), (bottom, right)]

                self.previous_face_points = face_points
                self.previous_face_box = face_box
            
            else: # fallback just so everything doesn't break
                face_points = self.previous_face_points
                face_box = self.previous_face_box

        return frame, face_points, face_box