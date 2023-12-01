import numpy as np
import cv2

from jetcam.csi_camera import CSICamera
import pyrealsense2 as rsx

class RealSenseCamera:
    def __init__(self):
        # Configure the camera settings for color and depth streams
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)  # Color stream configuration
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)   # Depth stream configuration

        # Initialize the pipeline for data flow
        self.pipeline = rs.pipeline()
        self.pipeline.start(self.config)  # Start the camera pipeline

    def get_images(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Captures and retrieves color and depth images from the camera.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the color image and the depth image.
                                           Returns (None, None) if frames are not available.
        """
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        # Check if both frames are available
        if not depth_frame or not color_frame:
            return None, None
        
        # Convert images to numpy arrays for processing
        color_image = np.asanyarray(color_frame.get_data())
        depth_color_frame = rs.colorizer().colorize(depth_frame)  # Colorize the depth frame for visualization
        depth_color_image = np.asanyarray(depth_color_frame.get_data())

        return color_image, depth_color_image  # Return the color and depth images

    def stop_streaming(self):
        """
        Stops the camera streaming.
        """
        self.pipeline.stop()  # Stop the camera pipeline


class MyCSICamera:
    def __init__(self, width: int = 640, height: int = 480):
        """
        Initializes the CSI camera with specified width and height.

        :param width: The width of the camera capture. Default is 640.
        :param height: The height of the camera capture. Default is 480.
        """
        # Initialize the CSI camera with specified width, height, and frame rate
        self.camera = CSICamera(width=width, height=height, capture_fps=30)
        self.camera.running = True  # Start the camera

    def get_images(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Captures a color image from the CSI camera.

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing the color image and a dummy depth image.
                                           The dummy depth image is a zero array with the same shape as the color image.
                                           Returns (None, None) if no image is captured.
        """
        # Read a frame from the camera
        color_image = self.camera.read()
        if color_image is None:
            return None, None  # Return None if no image is captured
        
        # Convert the color image from BGR to RGB format for consistency
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        # Create a dummy depth image (zero array with the same shape as the color image)
        depth_color_image = np.zeros_like(color_image)
        
        return color_image, depth_color_image  # Return the color and dummy depth images

    def stop_streaming(self):
        """
        Stops the camera streaming.
        """
        self.camera.running = False  # Stop the camera