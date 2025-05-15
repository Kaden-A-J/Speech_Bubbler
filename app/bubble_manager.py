import bubble_locator
import numpy as np
import cv2


BUBBLE_RECT_LOCATION_TETHER = 300
TEXT_OFFSET = 1.5


class bubble_manager():
    def __init__(self, bounding_box, transcript):
        self.bubble_locator = bubble_locator.bubble_locator(bounding_box)
        self.bubble_location = [0, 0]
        self.bounding_box = bounding_box
        self.transcript = transcript
        self.previous_bubble_size_location = (0, 0)
        self.previous_bubble_size_rect = [0, 0]
        self.bubble_center_offset_since_reset = (0, 0)
        self.bubble_rect = [[0, 0], [0, 0]]
        self.current_phrase = ''
        self.current_phrase_start = -1
        self.current_phrase_end = -1
        self.bubble_height = 0
        self.update_queued = True

        # font, font_scale, font_color, font_thickness
        self.font_info = [cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 0), 2]


    def project_bubble(self, frame, cap):
            
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)/1000


            # temp_text = f'{bubble_width}, {self.bubble_center_offset_since_reset}, the quick brown gray fox jumps over the lazy dog'
            if timestamp >= self.current_phrase_end:
                self.reset_current_phrase(timestamp)
                self.current_phrase = self.get_current_phrase(timestamp, self.transcript)

            bubble_rect_top_left, bubble_rect_bottom_right = self.get_bubble_rect()
            bubble_text = self.generate_text(self.current_phrase)

            cv2.rectangle(frame, bubble_rect_top_left, bubble_rect_bottom_right, (255, 255, 255), thickness=-1)

            font, font_scale, font_color, font_thickness = self.font_info
            text_height = cv2.getTextSize(bubble_text[0], font, font_scale, font_thickness)[0][1]
            text_offset = int(text_height * TEXT_OFFSET)

            self.bubble_height = bubble_rect_bottom_right[0] - bubble_rect_top_left[0]

            # print (text_offset * len(bubble_text), bubble_height)

            # if text_offset * len(bubble_text) > self.bubble_height:
            #     self.reset_current_phrase(timestamp)
            #     self.current_phrase = self.get_current_phrase(timestamp, self.transcript)

            for idx, text in enumerate(bubble_text):
                cv2.putText(frame, text, (bubble_rect_top_left[0], text_offset + bubble_rect_top_left[1] + (text_offset * idx)), font, font_scale, font_color, font_thickness)
        
            return frame


    def reset_current_phrase(self, timestamp):
        self.update_queued = True
        self.current_phrase = ''
        self.current_phrase_start = -1
        self.current_phrase_end = -1


    def get_current_phrase(self, timestamp, transcription):

            tracking = False
            ending = False
            curr_phrase = ''
            for segment in transcription['segments']:
                for word in segment['words']:
                    if timestamp > word['start'] and timestamp < word['end']:
                        if not tracking:
                            self.current_phrase_start = word['start']
                        tracking = True

                        curr_phrase = f'{curr_phrase} {word['word']}'

                    else:
                        if tracking:
                            new_phrase = f'{curr_phrase} {word['word']}'

                            font, font_scale, font_color, font_thickness = self.font_info
                            text_height = cv2.getTextSize('test', font, font_scale, font_thickness)[0][1]
                            text_offset = int(text_height * TEXT_OFFSET)

                            bubble_text = self.generate_text(new_phrase)

                            if (text_offset * len(bubble_text) > self.bubble_height):
                                ending = True
                                break

                            self.current_phrase_end = word['end']
                            curr_phrase = new_phrase

                            if ('.' in word['word']):
                                ending = True
                                self.current_phrase_end = word['end']
                                break
                if ending:
                    break
            
            # print(curr_phrase)
            return curr_phrase


    def generate_text(self, phrase):
        bubble_width = self.bubble_rect[1][0] - self.bubble_rect[0][0]
        
        font, font_scale, font_color, font_thickness = self.font_info

        raw_text = phrase.split()
        text_rows = []
        current_row = ''
        if len(raw_text) > 0 :
            current_row = raw_text[0]
        for word in raw_text[1:]:
            new_row = f'{current_row} {word}'
            if cv2.getTextSize(new_row, font, font_scale, font_thickness)[0][0] < bubble_width:
                current_row = new_row
                continue
                
            text_rows.append(current_row)
            current_row = word

        # the last row didn't overextend the width so manually add it to the list
        text_rows.append(current_row)

        return text_rows


    def get_bubble_rect(self):
        return self.bubble_rect


    def update(self, face_points, face_box, frame_no):
        self.bubble_locator.update(face_points)
        self.bubble_location = self.bubble_locator.get_bubble_location()

        self.bubble_center_offset_since_reset = (self.previous_bubble_size_location[0] - self.bubble_location[0],
                                            self.previous_bubble_size_location[1] - self.bubble_location[1])
        
        if self.update_queued:
            self.update_queued = False
            self.bubble_rect = self.update_bubble_size(face_points, face_box)
        else:
            self.bubble_rect = self.move_bubble_rect_center(self.previous_bubble_size_rect, self.bubble_center_offset_since_reset)

        
    def move_bubble_rect_center(self, previous_bubble_size_rect, bubble_center_offset_since_reset):
        new_top_left = [int(previous_bubble_size_rect[0][0] - bubble_center_offset_since_reset[0]), int(previous_bubble_size_rect[0][1] - bubble_center_offset_since_reset[1])]
        new_bottom_right = [int(previous_bubble_size_rect[1][0] - bubble_center_offset_since_reset[0]), int(previous_bubble_size_rect[1][1] - bubble_center_offset_since_reset[1])]
        new_bubble_rect = [new_top_left, new_bottom_right]
        return new_bubble_rect


    def update_bubble_size(self, face_points, face_box):

        width, height = self.bounding_box
        face_box_top_left, face_box_bottom_right = face_box


        # the percentage of space that should be left as a border between the speech bubble and the edge of the face and edge of the screen
        speech_bubble_border_scale = 0.2
        face_wall_x_distance = 0

        bubble_rect_top_left = None
        bubble_rect_bottom_right = None

        # TODO: make this track the currently talking face
        # splits the image into 4 triangular quadrants to determine the size of the bubble based on which side of the face it is on
        # top or bottom quadrant
        if np.abs(face_points[0][0] - self.bubble_location[0]) < np.abs(face_points[0][1] - self.bubble_location[1]):
            
            # bottom quadrant
            if self.bubble_location[1] > face_points[0][1]:

                face_wall_y_distance = np.abs(face_box_bottom_right[0] - height)
                bubble_rect_top_left = (int(width * speech_bubble_border_scale),
                                        int(face_box_bottom_right[0] + (face_wall_y_distance*speech_bubble_border_scale)))
                
                bubble_rect_bottom_right = (int(width - (width * speech_bubble_border_scale)),
                                            int(height - (face_wall_y_distance*speech_bubble_border_scale)))

            else: # top quadrant

                face_wall_y_distance = face_box_top_left[0]
                bubble_rect_top_left = (int(width * speech_bubble_border_scale),
                                        int(face_wall_y_distance*speech_bubble_border_scale))
                
                bubble_rect_bottom_right = (int(width - (width * speech_bubble_border_scale)),
                                            int(face_wall_y_distance - (face_wall_y_distance*speech_bubble_border_scale)))

        else: # left or right quadrant
            
            # right quadrant
            if self.bubble_location[0] > face_points[0][0]:

                face_wall_x_distance = np.abs(face_box_bottom_right[1] - width)
                bubble_rect_top_left = (int(face_box_bottom_right[1] + (face_wall_x_distance*speech_bubble_border_scale)),
                                        int(height*speech_bubble_border_scale))
                
                bubble_rect_bottom_right = (int(width - (face_wall_x_distance*speech_bubble_border_scale)),
                                        int(height - (height*speech_bubble_border_scale)))

            else: #left quadrant
                                
                face_wall_x_distance = face_box_top_left[1]
                bubble_rect_top_left = (int(face_wall_x_distance*speech_bubble_border_scale),
                                        int(height*speech_bubble_border_scale))
                
                bubble_rect_bottom_right = (int(face_wall_x_distance - (face_wall_x_distance*speech_bubble_border_scale)),
                                        int(height - (height*speech_bubble_border_scale)))


        # tether bubble to not be too far away from the bubble location
        if bubble_rect_top_left[0] < self.bubble_location[0] - BUBBLE_RECT_LOCATION_TETHER:
            bubble_rect_top_left = (int(self.bubble_location[0] - BUBBLE_RECT_LOCATION_TETHER), bubble_rect_top_left[1])
        if bubble_rect_top_left[1] < self.bubble_location[1] - BUBBLE_RECT_LOCATION_TETHER:
            bubble_rect_top_left = (bubble_rect_top_left[0], int(self.bubble_location[1] - BUBBLE_RECT_LOCATION_TETHER))
        
        if bubble_rect_bottom_right[0] > self.bubble_location[0] + BUBBLE_RECT_LOCATION_TETHER:
            bubble_rect_bottom_right = (int(self.bubble_location[0] + BUBBLE_RECT_LOCATION_TETHER), bubble_rect_bottom_right[1])
        if bubble_rect_bottom_right[1] > self.bubble_location[1] + BUBBLE_RECT_LOCATION_TETHER:
            bubble_rect_bottom_right = (bubble_rect_bottom_right[0], int(self.bubble_location[1] + BUBBLE_RECT_LOCATION_TETHER))

        self.previous_bubble_size_location = self.bubble_location
        self.previous_bubble_size_rect = [bubble_rect_top_left, bubble_rect_bottom_right]
        return [bubble_rect_top_left, bubble_rect_bottom_right]