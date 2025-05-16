# Takes a video file, isolates who is talking, then generates a speech bubble with subtitles

#✅ Input video file

#✅ Generate text of what is being said

# Identify and isolate the location of people in shot
# - Give each person a unique label to keep track of them between frames

# Determine who it talking
# - See if lips are moving
# - Speech recognition to identify who is talking if can't see lips
#   - Will have to see lips moving while talking (or being the only person in shot) to initially identify

#✅ Make a speech bubble that tries not to overlap people

#✅ Generate subtitles real time in the speech bubble

#✅ Make README

import cv2
import speech_manager
import face_tracking
import bubble_manager
import moviepy as mp
import os


VERBOSE = True
VISUAL_DEBUG = False


video_names = []
video_paths = []
audio_paths = []
output_paths = []
for c_video_name in os.listdir('./INPUT_CLIPS/'):
    if '.mp4' not in c_video_name[-4:]:
        continue
    no_extension_vid_name = c_video_name[:-4]
    video_names.append(no_extension_vid_name)
    video_paths.append(f'./INPUT_CLIPS/{no_extension_vid_name}.mp4')
    output_paths.append(f'./OUTPUT_CLIPS/{no_extension_vid_name}_processed.mp4')
    audio_paths.append(f'./temp/{no_extension_vid_name}.wav')

print(f'videos found: {video_names}')

if not os.path.exists(f'./temp/'):
    os.mkdir(f'./temp/')
if not os.path.exists(f'./INPUT_CLIPS/'):
    os.mkdir(f'./INPUT_CLIPS/')
if not os.path.exists(f'./OUTPUT_CLIPS/'):
    os.mkdir(f'./OUTPUT_CLIPS/')


def __main__(video_name, video_path, output_path, audio_path):
    cap = cv2.VideoCapture(video_path)

    bounding_box = [cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)]
    fps = cap.get(cv2.CAP_PROP_FPS)
    audioless_path = f'./temp/{video_name}_audioless.mp4'
    writer = cv2.VideoWriter(audioless_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(bounding_box[0]), int(bounding_box[1])))

    _face_tracker = face_tracking.face_tracker()
    transcription = speech_manager.transcribe_file(video_path, audio_path)
    _bubble_manager = bubble_manager.bubble_manager(bounding_box, transcription)

    text = ''
    frame_no = 0
    total_frames = frame_count(video_path)
    while(cap.isOpened()):
        if VERBOSE:
            if frame_no % int(total_frames/100) == 0:
                print(f'{video_name} frame: {frame_no} / {total_frames}')

        frame_exists, frame = cap.read()

        if frame_exists:
            frame, face_points, (face_box_top_left, face_box_bottom_right) = _face_tracker.project_face_tracking(frame, frame_no=frame_no, features=False, box=True, debug=VISUAL_DEBUG)

            _bubble_manager.update(face_points, [face_box_top_left, face_box_bottom_right], frame_no)

            frame = _bubble_manager.project_bubble(frame, cap)

            if VISUAL_DEBUG:
                for point in face_points:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 255, 0), -1)

                for point in _bubble_manager.bubble_locator.points:
                    cv2.circle(frame, (int(point[0]), int(point[1])), 10, (0, 0, 255), -1)

                cv2.circle(frame, (int(_bubble_manager.bubble_locator.smoothed_furthest_point[0]), int(_bubble_manager.bubble_locator.smoothed_furthest_point[1])), 10, (255, 0, 0), -1)
                cv2.circle(frame, (int(_bubble_manager.bubble_locator.furthest_point[0]), int(_bubble_manager.bubble_locator.furthest_point[1])), 10, (255, 255, 0), -1)

                frame = speech_manager.project_speech_recognition(frame, cap, transcription, frame_no)

            writer.write(frame)

        else:
            break
        frame_no += 1


    writer.release()

    cap.release()
    cv2.destroyAllWindows()


    audio = mp.AudioFileClip(audio_path)
    video = mp.VideoFileClip(audioless_path)
    video.audio = audio

    video.write_videofile(output_path)

    if os.path.exists(audioless_path):
        os.remove(audioless_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)


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



for idx, vid in enumerate(video_names):
    __main__(video_names[idx], video_paths[idx], output_paths[idx], audio_paths[idx])
