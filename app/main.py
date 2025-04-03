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
import speech_recog
import face_tracking
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

frames = []
frame_no = 0
total_frames = frame_count(video_path)
while(cap.isOpened()):
    if frame_no % int(total_frames/100) == 0:
        print(f'frame: {frame_no} / {total_frames}')

    start_time = time.time()
    frame_exists, frame = cap.read()

    if frame_exists:
        
        frame = face_tracking.project_face_tracking(frame, features=False)

        frame = speech_recog.project_speech_recognition(frame, cap, transcription, frame_no)

        frames.append(frame)

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


width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

newframes = []
writer = cv2.VideoWriter('audioless.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height)))

for i in range(0, len(frames)):
    newframes.append(frames[i])
    writer.write(frames[i])  # write frame into output vid

writer.release()

cap.release()
cv2.destroyAllWindows()


audio = mp.AudioFileClip(audio_path)
video = mp.VideoFileClip('audioless.mp4')
video.audio = audio

video.write_videofile(f'app/res/processed/{video_name}-processed.mp4')

if os.path.exists('audioless.mp4'):
    os.remove('audioless.mp4')