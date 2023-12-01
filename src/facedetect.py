import cv2

import torch
from facenet_pytorch import MTCNN

class FaceDetector:
    def __init__(self):
        """
        Initializes the FaceDetector with an MTCNN model.
        """
        self.mtcnn = MTCNN(keep_all=True)  # Initialize MTCNN with the option to keep all detected faces

    def detect_faces_from_color_image(self, color_image: torch.Tensor) -> tuple:
        """
        Detects faces in a given color image using MTCNN.

        :param color_image: The color image as a PyTorch Tensor.
        :return: A tuple containing:
                 - boxes: The bounding boxes of detected faces.
                 - face_images: A list of cropped images of detected faces.
        """
        # Detect faces and their bounding boxes in the image
        boxes, probs = self.mtcnn.detect(color_image)
        face_images = []  # List to store cropped face images
        h, w, _ = color_image.shape  # Get the height and width of the image

        if boxes is not None:
            for box in boxes:
                # Calculate coordinates for the bounding box with some padding
                x1, y1, x2, y2 = max(0, int(box[0]-20)), max(0, int(box[1]-20)), min(w, int(box[2]+20)), min(h, int(box[3]+20))
                # Draw the bounding box on the image
                cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Crop and append the face image to the list
                face_images.append(color_image[y1:y2, x1:x2])

        return boxes, face_images  # Return the bounding boxes and cropped face images
