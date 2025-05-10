import numpy as np
import math


# how many frames the bubble will 'stall' in place if the furthest point instantaneously moves a large distance
# so the bubble won't jitter from one side of the screen to the other
BUBBLE_FAR_MOVEMENT_FRAMES = 60


class bubble_locator():

    def __init__(self, bounding_box, num_points=32):
        
        self.REPULSION_SCALE = 300
        self.frame_count = 0
        self.num_points = num_points
        self.bounding_box = None
        self.points = None
        self.furthest_point = (-1, -1)
        self.smoothed_furthest_point = (-1, -1)
        self.bubble_far_movement_counter = 0
        self.bounding_box = bounding_box


    def reset_points(self, num_points):
        self.bounding_box = self.bounding_box
        self.points = self.distribute_points(self.bounding_box[0], self.bounding_box[1], num_points, 0.1)


    def update(self, face_points):
        if self.frame_count % 60 == 0:
            self.reset_points(self.num_points)

            for i in range(100):
                self.settle_points(face_points)
        
        self.settle_points(face_points)

        new_furthest_point = self.find_furthest_point(face_points)
        
        if self.furthest_point[0] == -1 and self.furthest_point[1] == -1:
            self.furthest_point = new_furthest_point

        furthest_points_difference = np.abs(np.sqrt(new_furthest_point[0]**2 + new_furthest_point[1]**2) - np.sqrt(self.furthest_point[0]**2 + self.furthest_point[1]**2))

        # if the new_furthest_point is out of range for BUBBLE_FAR_MOVEMENT_FRAMES then just reset the smoothed point to the new furthest point
        if furthest_points_difference > np.abs(np.sqrt(self.bounding_box[0]**2 + self.bounding_box[1]**2)) / 4:
            # don't update furthest point
            self.bubble_far_movement_counter += 1
            if self.bubble_far_movement_counter >= BUBBLE_FAR_MOVEMENT_FRAMES:
                self.smoothed_furthest_point = new_furthest_point
                self.bubble_far_movement_counter = 0
        else:
            self.furthest_point = new_furthest_point
            self.bubble_far_movement_counter = 0
        
        # if smoothed_furthest_point isn't initialized then just set it to the current furthest point
        if self.smoothed_furthest_point[0] == -1 and self.smoothed_furthest_point[1] == -1:
            self.smoothed_furthest_point = self.furthest_point
        else:
            # slowly shove smoothed_furthest_point towards furthest_point
            self.smoothed_furthest_point = self.pull_point_dynamic(self.furthest_point, self.smoothed_furthest_point, 1, 0.01)

        self.frame_count += 1
    

    def get_bubble_location(self):
        return self.smoothed_furthest_point


    def find_furthest_point(self, face_points):
        furthest_distance = 0
        furthest_point = None
        for point in self.points:
            curr_distance = 0
            for face_point in face_points:
                abs_point_diff = np.abs(face_point - point)
                curr_distance += math.sqrt(abs_point_diff[0]**2 + abs_point_diff[1]**2)

            if curr_distance > furthest_distance:
                furthest_distance = curr_distance
                furthest_point = point
        
        return furthest_point
            


    def shove_point_dynamic(self, point1, point2, base_distance, scaling_factor):

        # Calculate the direction vector from point1 to point2
        direction_x = point2[0] - point1[0]
        direction_y = point2[1] - point1[1]
        
        # Calculate the magnitude of the direction vector
        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        
        # Avoid division by zero (if both points overlap)
        if magnitude == 0:
            return point2

        # Normalize the direction vector
        normalized_x = direction_x / magnitude
        normalized_y = direction_y / magnitude
        
        # Adjust the shove distance based on the distance between the points
        dynamic_distance = base_distance * (scaling_factor / magnitude)
        
        # Move point2 farther away by the calculated distance
        new_point2 = (
            point2[0] + (normalized_x * dynamic_distance),
            point2[1] + (normalized_y * dynamic_distance)
        )
        
        return new_point2
    

    def pull_point_dynamic(self, point1, point2, base_distance, scaling_factor):

        direction_x = point2[0] - point1[0]
        direction_y = point2[1] - point1[1]

        magnitude = math.sqrt(direction_x**2 + direction_y**2)
        
        if magnitude == 0:
            return point2

        normalized_x = direction_x / magnitude
        normalized_y = direction_y / magnitude

        dynamic_distance = base_distance * (scaling_factor * magnitude)

        new_point2 = (
            point2[0] - (normalized_x * dynamic_distance),
            point2[1] - (normalized_y * dynamic_distance)
        )
        
        return new_point2


    def settle_points(self, face_points):

        for i, point in enumerate(self.points):

            base_distance = 25
            scaling_factor = 100

            temp_point = (0, 0)
            temp_point += self.shove_point_dynamic((self.points[i][0], 0), self.points[i], base_distance, scaling_factor) - self.points[i]
            temp_point += self.shove_point_dynamic((0, self.points[i][1]), self.points[i], base_distance, scaling_factor) - self.points[i]
            temp_point += self.shove_point_dynamic((self.points[i][0], self.bounding_box[1]), self.points[i], base_distance, scaling_factor) - self.points[i]
            temp_point += self.shove_point_dynamic((self.bounding_box[0], self.points[i][1]), self.points[i], base_distance, scaling_factor) - self.points[i]

            for j, face_point in enumerate(face_points):
                temp_point += self.shove_point_dynamic(face_point, self.points[i], base_distance, scaling_factor) - self.points[i]

            self.points[i] += temp_point

            self.points[i][0] = np.clip(self.points[i][0], 0, self.bounding_box[0])
            self.points[i][1] = np.clip(self.points[i][1], 0, self.bounding_box[1])


    def distribute_points(self, width, height, num_points, edge_distance):
        """
        Distributes points evenly within a rectangle.

        Args:
            width (float): Width of the rectangle.
            height (float): Height of the rectangle.
            num_points (int): Number of points to distribute.

        Returns:
            numpy.ndarray: Array of shape (num_points, 2) containing the (x, y) coordinates of the points.
        """

        x_count = int(np.sqrt(num_points * width / height))
        y_count = int(num_points / x_count)

        x_coords = np.linspace(width * edge_distance, width - (width * edge_distance), x_count)
        y_coords = np.linspace(height * edge_distance, height - (height * edge_distance), y_count)

        x_grid, y_grid = np.meshgrid(x_coords, y_coords)

        points = np.stack([x_grid.ravel(), y_grid.ravel()], axis=-1)

        return points[:num_points]