import os
import numpy as np
import yaml,glob
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
from PIL import Image, ImageTk

from src.camera import RealSenseCamera,MyCSICamera
from src.facedetect import FaceDetector

class RealTimeAnnotationApp(tk.Tk):
    def __init__(self, detector, config_data: dict):
        """
        Initializes the Real-Time Annotation App.

        :param detector: A list containing a camera object and a face detector object.
        :param config_data: Configuration data containing annotations information.
        """
        super().__init__()
        self.detector = detector
        self.title('Real-Time Annotation App')  # Set the title of the window
        self.protocol('WM_DELETE_WINDOW', self.on_closing)  # Define window close protocol

        # Storing the configuration data
        self.config_data = config_data

        # Creating a canvas for displaying the video feed
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()

        # Creating a frame for buttons
        buttons_frame = tk.Frame(self)
        buttons_frame.pack()

        # Creating buttons for annotations and storing them
        self.buttons = {}
        for annotation in self.config_data['annotations']:
            button = tk.Button(buttons_frame, text=annotation['name'],
                               command=lambda ann=annotation: self.save_face(ann))
            button.pack(side=tk.LEFT)
            self.buttons[annotation['name']] = annotation['folder']

        # List to store face images
        self.face_images = []
        self.update_canvas()  # Start updating the canvas

    def update_canvas(self):
        """
        Updates the canvas with the latest frame from the camera and detected faces.
        """
        # Get the current frame from the camera
        color_image, _ = self.detector[0].get_images()  # Use index 0 for camera
        # Detect faces in the current frame
        _, self.face_images = self.detector[1].detect_faces_from_color_image(color_image)  # Use index 1 for face_detector
        # Convert the image for Tkinter compatibility
        self.photo_image = Image.fromarray(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))  # Convert to RGB
        self.photo_image = ImageTk.PhotoImage(self.photo_image)  # Convert to Tkinter PhotoImage
        # Display the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        # Schedule the next canvas update
        self.after(10, self.update_canvas)

    def save_face(self, annotation: dict):
        """
        Saves detected face images to the specified annotation folder.

        :param annotation: A dictionary containing the name and folder of the annotation.
        """
        # Define the folder path for saving face images
        folder = os.path.join('..', 'data', annotation['folder'])
        os.makedirs(folder, exist_ok=True)  # Create the folder if it doesn't exist

        # Find the next index for saving the image
        existing_files = glob.glob(os.path.join(folder, f"{annotation['folder']}_*.png"))
        next_index = len(existing_files)

        # Save face images if any are detected
        if self.face_images:
            for idx, face_img in enumerate(self.face_images, start=next_index):
                file_path = os.path.join(folder, f"{annotation['folder']}_{idx}.png")
                cv2.imwrite(file_path, face_img)
            messagebox.showinfo('Info', f'Faces saved in {folder} folder')
        else:
            messagebox.showwarning('Warning', 'No faces detected')

    def on_closing(self):
        """
        Defines actions to be taken when the application window is closed.
        """
        self.detector[0].stop_streaming()  # Stop the camera streaming
        self.destroy()  # Close the application window

if __name__ == '__main__':
    # Load configuration from the YAML file
    with open('config/annotation_config.yaml', 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Determine the type of camera to use from the configuration
    camera_type = config_data.get('camera', 'RealSense').lower()
    
    # Create instances of the camera and face detector based on the configuration
    if camera_type == 'realsense':
        # Initialize a RealSense camera if configured
        camera = RealSenseCamera()
    elif camera_type == 'csi':
        # Initialize a CSI camera if configured
        camera = MyCSICamera()
    else:
        # Raise an error if the camera type is unknown
        raise ValueError(f'Unknown camera type: {camera_type}')
    
    # Initialize the face detector
    face_detector = FaceDetector()
    
    # Create an instance of the RealTimeAnnotationApp with the camera and face detector
    app = RealTimeAnnotationApp((camera, face_detector), config_data)
    # Run the application's main loop
    app.mainloop()