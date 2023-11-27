import os
import numpy as np
import torch
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import imutils 
# Class for CROP and ROTATE the DOT

class DOTCrop:
    def __init__(self,) -> None:
        models_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Models")
        self.model = YOLO(os.path.join(models_path, "find_tyre_center.pt"))
        self.threshold = 0.8
        self.index = 0
    
    def get_box(self, box):
        if len(box.xywh) > 2:
            all_boxes = box.xywh

            img_size = np.array(box.orig_shape) / 2
            # Initialize the minimum distance to a large number
            min_distance = float('inf')
            # Initialize the closest group to None
            closest_group = None

            # Split the list into groups of 2
            groups = all_boxes.split(2)

            # For each group
            for group in groups:
                # Calculate the Euclidean distance between the first two values of the group and the given values
                distance = torch.norm(group.mean(dim=0)[:2].cpu() - img_size)
                # If this distance is smaller than the current minimum distance
                if distance < min_distance:
                    # Update the minimum distance and the closest group
                    min_distance = distance
                    closest_group = group


            b1, b2 = closest_group

            if(b1[2].item() > b2[2].item()):
                return b1, b2
            else:
                return b2, b1
        else:
            b1, b2 = box.xywh
            if(b1[2].item() > b2[2].item()):
                return b1, b2
            else:
                return b2, b1

    def find_center(self, image):
        results = self.model(image)[0]
        bbox = results.boxes

        box_maior, box_menor = self.get_box(bbox)

        x, y, w, h = box_maior.cpu().numpy().astype(int)
        #_, _, w1, h1 = box_menor.cpu().numpy().astype(int)

        return x, y

    def calculate_angle(self, points):
        p_line1, p_common, p_line2 = points

        vector1 = np.array(p_line1) - np.array(p_common)
        vector2 = np.array(p_line2) - np.array(p_common)
        
        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)
        cos_angle = dot_product / (magnitude1 * magnitude2)
        
        angle_radians = np.arccos(cos_angle)
        angle_degrees = np.degrees(angle_radians)
        
        # Determinando a orientação das retas
        cross_product = np.cross(vector1, vector2)
        
        if cross_product < 0:
            angle_degrees = -angle_degrees
        
        return angle_degrees
    
    def rotate_dot(self, dot_img, dotCenter, tire_center, top_center):
        final_angle = self.calculate_angle([top_center, tire_center, dotCenter])

        rotated_image = Image.fromarray(dot_img).rotate(final_angle, expand=True)

        return rotated_image

    def cropDot(self, image, bouding_boxes):
        # Find Tire Center
        xcentro, ycentro = self.find_center(image)

        # Crop dot
        x1, y1, x2, y2, score, class_id = bouding_boxes[0]
        padding_size = 30
        padded_top_left = (max(0, x1 - padding_size), max(0, y1 - padding_size))
        padded_bottom_right = (min(image.shape[1], x2 + padding_size), min(image.shape[1], y2 + padding_size))
        dot_img = image[padded_top_left[1]:padded_bottom_right[1], padded_top_left[0]:padded_bottom_right[0]]

        xdot = (x1 + x2) / 2
        ydot = (y1 + y2) / 2
        dotCenter = xdot, ydot
        tire_center = xcentro, ycentro
        top_center = xcentro, 0.0

        rotated_image = self.rotate_dot(dot_img, dotCenter, tire_center, top_center)
        #rotated_image.save(f"./Results/img{self.index}.png")
        #self.index += 1
        return rotated_image