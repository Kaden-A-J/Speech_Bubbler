# Takes a video file, isolates who is talking, then generates a speech bubble with subtitles

#✅ Input video file

#✅ Generate text of what is being said

# Identify and isolate the location of people in shot
# - Give each person a unique lable to keep track of them between frames

# Determine who it talking
# - See if lips are moving
# - Speech recognition to identify who is talking if can't see lips
#   - Will have to see lips moving while talking (or being the only person in shot) to initially identify

# Make a speech bubble that tries not to overlap people

# Generate subtitles real time in the speech bubble

#✅ Make README

import cv2
import speech_recog
import face_tracking
import bubble_locator
import time
import moviepy as mp
import os


def frame_count(video_path, manual=False):
    def manual_count(handler):
        frames = 0
        while True:
            status, frame = handler.read()
            if not status:
                break
            frames += 1
        return frames 

    cap = cv2.VideoCapture(video_path)
    # Slow, inefficient but 100% accurate method 
    if manual:
        frames = manual_count(cap)
    # Fast, efficient but inaccurate method
    else:
        try:
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        except:
            frames = manual_count(cap)
    cap.release()
    return frames


video_name = 'moby_dick_10sec'
video_path = f'./app/res/video/{video_name}.mp4'
audio_path = f'./app/res/audio/{video_name}.wav'

transcription = speech_recog.transcribe_file(video_name=video_name)

cap = cv2.VideoCapture(video_path)

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)
writer = cv2.VideoWriter('audioless.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height)))

_bubble_locator = bubble_locator.bubble_locator()
_face_tracker = face_tracking.face_tracker()

frame_no = 0
total_frames = frame_count(video_path)
while(cap.isOpened()):
    if frame_no % int(total_frames/100) == 0:
        print(f'frame: {frame_no} / {total_frames}')

    start_time = time.time()
    frame_exists, frame = cap.read()

    if frame_exists:
        
        frame, face_points, (face_box_top_left, face_box_bottom_right) = _face_tracker.project_face_tracking(frame, features=False)

        height, width, channels = frame.shape
        _bubble_locator.update(face_points, [width, height])
        bubble_location = _bubble_locator.get_bubble_location()

        # the percentage of space that should be left as a border between the speech bubble and the edge of the face and edge of the screen
        speech_bubble_border_scale = 0.1
        face_wall_x_distance = 0

        # TODO: make this track the currently talking face
        if bubble_location[0] < face_points[0][0]:
            face_wall_x_distance = face_box_top_left[0]
        else:
            face_wall_x_distance = width - face_box_bottom_right[1]
        
        bubble_rec_top_left = (int(bubble_location[0] - (face_wall_x_distance/2) + (face_wall_x_distance*speech_bubble_border_scale)),
                                int(bubble_location[1] - 300))
        
        bubble_rec_bottom_right = (int(bubble_location[0] + (face_wall_x_distance/2) - (face_wall_x_distance*speech_bubble_border_scale)),
                                    int(bubble_location[1] + 300))

        cv2.rectangle(frame, bubble_rec_top_left, bubble_rec_bottom_right, (255, 255, 255), thickness=-1)


        for point in face_points:
            cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 255, 0), -1)
        # print(_bubble_locator.points)

        for point in [bubble_location]:
            cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 0, 255), -1)

        frame = speech_recog.project_speech_recognition(frame, cap, transcription, frame_no)

        writer.write(frame)

        # cv2.imshow('frame',frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        
        # # cap framerate
        # end_time = time.time()
        # time_diff = end_time - start_time
        # fps_ms = cap.get(cv2.CAP_PROP_FPS)/1000
        # if time_diff < fps_ms:
        #     time.sleep(fps_ms - time_diff)

    else:
        break
    frame_no += 1


writer.release()

cap.release()
cv2.destroyAllWindows()


audio = mp.AudioFileClip(audio_path)
video = mp.VideoFileClip('audioless.mp4')
video.audio = audio

video.write_videofile(f'app/res/processed/{video_name}_processed.mp4')

if os.path.exists('audioless.mp4'):
    os.remove('audioless.mp4')