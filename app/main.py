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
import speech_manager
import face_tracking
import bubble_manager
import time
import moviepy as mp
import os


VERBOSE = True


video_name = 'moby_dick_10sec'
video_path = f'./app/res/video/{video_name}.mp4'
audio_path = f'./app/res/audio/{video_name}.wav'


def __main__():
    cap = cv2.VideoCapture(video_path)

    bounding_box = [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]
    fps = cap.get(cv2.CAP_PROP_FPS)
    writer = cv2.VideoWriter('audioless.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(bounding_box[0]), int(bounding_box[1])))


    _face_tracker = face_tracking.face_tracker()
    _bubble_manager = bubble_manager.bubble_manager(bounding_box)
    transcription = speech_manager.transcribe_file(video_name=video_name)


    frame_no = 0
    total_frames = frame_count(video_path)
    while(cap.isOpened()):
        if VERBOSE:
            if frame_no % int(total_frames/100) == 0:
                print(f'frame: {frame_no} / {total_frames}')

        frame_exists, frame = cap.read()

        if frame_exists:
            frame, face_points, (face_box_top_left, face_box_bottom_right) = _face_tracker.project_face_tracking(frame, frame_no=frame_no, features=False)

            _bubble_manager.update(face_points, [face_box_top_left, face_box_bottom_right])
            bubble_rect_top_left, bubble_rect_bottom_right = _bubble_manager.get_bubble_rect()

            cv2.rectangle(frame, bubble_rect_top_left, bubble_rect_bottom_right, (255, 255, 255), thickness=-1)

            for point in face_points:
                cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 255, 0), -1)

            # for point in _bubble_locator.points:
            #     cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 0, 255), -1)

            # cv2.circle(frame, (int(_bubble_locator.smoothed_furthest_point[0]), int(_bubble_locator.smoothed_furthest_point[1])), 10, (255, 0, 0), -1)
            # cv2.circle(frame, (int(_bubble_locator.furthest_point[0]), int(_bubble_locator.smoothed_furthest_point[1])), 10, (255, 255, 0), -1)

            frame = speech_manager.project_speech_recognition(frame, cap, transcription, frame_no)

            writer.write(frame)

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


__main__()