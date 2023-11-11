import os
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO


class DOTDetect:
    def __init__(self, resized_video_width, resized_video_height) -> None:
        self.resized_video_height = resized_video_height
        self.resized_video_width = resized_video_width

        models_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Models")
        self.model = YOLO(os.path.join(models_path, "dot_detect.pt"))
        self.threshold = 0.5
    
    def show_dot(self, ret, frame):
        if not ret:
            return None, None, None
        
        results = self.model(frame)[0]
        all_bboxes = []

        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            if score > self.threshold:
                all_bboxes.append([int(x1), int(y1), int(x2), int(y2), score, class_id])
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

        # Convert the image from OpenCV BGR format to PIL RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original_frame = frame.copy()
        # Resize
        frame = cv2.resize(frame, (self.resized_video_width, self.resized_video_height))
        # Convert the image to PIL format
        image = Image.fromarray(frame)
        # Convert the image to ImageTk format
        image = ImageTk.PhotoImage(image)
        # Update the image display
        

        return image, all_bboxes, original_frame