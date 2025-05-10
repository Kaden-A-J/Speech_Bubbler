import bubble_locator
import numpy as np


BUBBLE_RECT_LOCATION_TETHER = 300


class bubble_manager():
    def __init__(self, bounding_box):
       self.bubble_locator = bubble_locator.bubble_locator(bounding_box)
       self.bubble_location = [0, 0]
       self.bounding_box = bounding_box
    

    def get_bubble_rect(self):
        return self.bubble_location


    def update(self, face_points, face_box):
        self.bubble_locator.update(face_points)
        self.bubble_location = self.bubble_locator.get_bubble_location()

        width, height = self.bounding_box
        face_box_top_left, face_box_bottom_right = face_box


        # the percentage of space that should be left as a border between the speech bubble and the edge of the face and edge of the screen
        speech_bubble_border_scale = 0.2
        face_wall_x_distance = 0

        bubble_rect_top_left = None
        bubble_rect_bottom_right = None

        # TODO: move this into a bubble manager class
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
        
        self.bubble_location = [bubble_rect_top_left, bubble_rect_bottom_right]