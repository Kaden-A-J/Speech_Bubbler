from moviepy import VideoFileClip
import whisper
import cv2
import os


def transcribe_file(video_name, verbose=False):
    video_path = f'res/video/{video_name}.mp4'
    audio_path = f'res/audio/{video_name}.wav'

    if not os.path.exists(video_path):
        print('input file not found')
        exit()
    if not os.path.exists(audio_path):
        audioclip = VideoFileClip(video_path)
        audioclip.audio.write_audiofile(audio_path)


    model = whisper.load_model('small.en')
    results = model.transcribe(audio=audio_path, word_timestamps=True)

    if verbose:
        for segment in results['segments']:
            print(''.join(f"{word['word']}[{word['start']}/{word['end']}]" 
                            for word in segment['words']))
        
    return results


def project_speech_recognition(frame, video_capture, transcription, frame_no=0, frame_info=True, word_info=True):
        curr_timestamp = video_capture.get(cv2.CAP_PROP_POS_MSEC)/1000

        curr_word = ''
        word_found = False
        for segment in transcription['segments']:
            for word in segment['words']:
                if curr_timestamp > word['start'] and curr_timestamp < word['end']:
                    curr_word = word['word']
                    word_found = True
                    break
            if word_found:
                break

        font                   = cv2.FONT_HERSHEY_SIMPLEX
        fontScale              = 2
        fontColor              = (255,255,255)
        thickness              = 3
        lineType               = 2

        text_y = 60
        if frame_info:
            cv2.putText(frame,f"frame: {str(frame_no)} - timestamp: {str(curr_timestamp)}", 
                (10,text_y), 
                font, 
                fontScale,
                fontColor,
                thickness,
                lineType)
            text_y += 60
        
        if word_info:
            cv2.putText(frame,f"current word: {curr_word}", 
                (10,text_y), 
                font, 
                fontScale,
                fontColor,
                thickness,
                lineType)
            text_y += 60

        return frame