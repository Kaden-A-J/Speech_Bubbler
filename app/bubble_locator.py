import numpy as np


class bubble_locator():

    def __init__(self, num_points=32):
        
        self.REPULSION_SCALE = 300
        self.frame_count = 0
        self.num_points = num_points
        self.bounding_box = None
        self.points = None
        self.furthest_point = None
        self.smoothed_furthest_point = (-1, -1)


    def reset_points(self, bounding_box, num_points):
        self.bounding_box = bounding_box
        self.points = self.distribute_points(self.bounding_box[0], self.bounding_box[1], num_points, 0.1)


    def update(self, face_points, bounding_box):
        if self.frame_count % 100 == 0:
            self.reset_points(bounding_box, self.num_points)

            for i in range(200):
                self.settle_points(face_points)
        
        self.settle_points(face_points)

        self.furthest_point = self.find_furthest_point(face_points)
        
        # if smoothed_furthest_point isn't initialized then just set it to the current furthest point
        if self.smoothed_furthest_point[0] == -1 and self.smoothed_furthest_point[1] == -1:
            self.smoothed_furthest_point = self.furthest_point
        else:
            # slowly shove smoothed_furthest_point towards furthest_point
            self.smoothed_furthest_point = self.shove_point_dynamic(self.furthest_point, self.smoothed_furthest_point, 1, -0.1)

        self.frame_count += 1
    

    def get_bubble_location(self):
        return self.smoothed_furthest_point


    def find_furthest_point(self, face_points):
        furthest_distance = 0
        furthest_point = None
        for point in self.points[1:]:
            curr_distance = 0
            for face_point in face_points:
                abs_point_diff = np.abs(face_point - point)
                curr_distance += (abs_point_diff[0] + abs_point_diff[1])

            if curr_distance > furthest_distance:
                curr_distance = furthest_distance
                furthest_point = point
        
        return furthest_point
            


    def shove_point_dynamic(self, point1, point2, base_distance, scaling_factor):
        import math

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
            point2[0] + normalized_x * dynamic_distance,
            point2[1] + normalized_y * dynamic_distance
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