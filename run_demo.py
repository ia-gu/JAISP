import os
import numpy as np
import random
import yaml
import glob
import tkinter as tk
import cv2
from PIL import Image, ImageTk
from einops import rearrange

import torch
from torchvision import transforms
import torchvision.transforms.functional as TF

import sys
sys.path.append('../')
from tester import Tester
from src.camera import RealSenseCamera, MyCSICamera
from src.facedetect import FaceDetector

class RealTimeTestApp(tk.Tk):
    def __init__(self, detector, config_data: dict):
        """
        Initializes the Real-Time Test App.

        :param detector: A tuple containing a camera object and a face detector object.
        :param config_data: Configuration data containing annotations information.
        """
        super().__init__()
        self.detector = detector
        self.title('Real-Time Annotation App')  # Set the title of the window
        self.protocol('WM_DELETE_WINDOW', self.on_closing)  # Define window close protocol

        # Store annotation information from configuration data
        self.annotations = config_data['annotations']

        # Set up a label for displaying the current annotation
        self.annotation_label = tk.Label(self, text='', font=('Helvetica', 16))
        self.annotation_label.pack()

        # Create a canvas for displaying the video feed
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()

        # Labels for displaying logits and results
        self.logits_label = tk.Label(self, text='', font=('Helvetica', 12))
        self.logits_label.pack()
        self.result_label = tk.Label(self, text='', font=('Helvetica', 12))
        self.result_label.pack()

        # Initialize the tester object for processing images
        self.tester = Tester()

        # List to store face images
        self.face_images = []
        self.update_canvas()  # Start updating the canvas

    def update_canvas(self):
        """
        Updates the canvas with the latest frame from the camera and processed faces.
        """
        # Get the current frame from the camera
        color_image, _ = self.detector[0].get_images()
        # Detect faces in the current frame
        _, self.face_images = self.detector[1].detect_faces_from_color_image(color_image)
        
        # Convert the image for Tkinter compatibility and display it
        self.photo_image = Image.fromarray(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
        self.photo_image = ImageTk.PhotoImage(self.photo_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

        # Process detected faces and update labels with results
        if self.face_images:
            self.face_image = cv2.cvtColor(self.face_images[0], cv2.COLOR_BGR2RGB)
            self.face_image = Image.fromarray(self.face_image)
            self.face_image.save('test.png', quality=100)
            # Transform the image for testing
            self.transform = transforms.Compose([transforms.Resize([144, 144]), transforms.ToTensor(), transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])])
            self.face_image = self.transform(self.face_image)

            # Rearrange the image tensor
            self.face_image = rearrange(self.face_image, 'c h w -> 1 c h w')
            print(self.face_image.shape)
            # Perform testing and get results
            test_results, logits = self.tester.test(self.face_image)

            # Update the annotation label based on the test results
            if test_results in range(len(self.annotations)):
                self.annotation_label.config(text=self.annotations[test_results]['name'])
            else:
                self.annotation_label.config(text='Unknown')
                
            # Update the logits and result labels
            self.logits_label.config(text=f'Logits: {" ".join(map(str, logits))}')
            self.result_label.config(text=f'Result: {test_results}')

        # Schedule the next canvas update
        self.after(10, self.update_canvas)

    def on_closing(self):
        """
        Defines actions to be taken when the application window is closed.
        """
        self.detector[0].stop_streaming()  # Stop the camera streaming
        self.destroy()  # Close the application window

if __name__ == '__main__':
    # Load configuration data from a YAML file
    with open('config/camera_config.yaml', 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Determine the type of camera to use based on the configuration
    camera_type = config_data.get('camera', 'RealSense').lower()
    # Instantiate the appropriate camera object based on the configuration
    if camera_type == 'realsense':
        # Initialize a RealSense camera if configured
        camera = RealSenseCamera()
    elif camera_type == 'csi':
        # Initialize a CSI camera if configured
        camera = MyCSICamera()
    else:
        # Raise an error if the specified camera type is not recognized
        raise ValueError(f'Unknown camera type: {camera_type}')
    
    # Initialize the face detector
    face_detector = FaceDetector()
    
    # Create an instance of the RealTimeTestApp with the camera and face detector
    app = RealTimeTestApp((camera, face_detector), config_data)
    # Start the application's main event loop
    app.mainloop()