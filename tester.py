import torch
import torchvision.transforms.functional as TF

import numpy as np
import random
import os
import sys

from src.vgg_local import VGG_LOCAL

class Tester:
    def __init__(self):
        """
        Initializes the Tester class which handles the testing of images using a trained model.
        """
        # Determine if CUDA (GPU support) is available and set the device accordingly
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize the model and move it to the appropriate device (GPU or CPU)
        self.model = VGG_LOCAL('VGG19', classes=3, image_size=144).to(self.device)

        # Load the pre-trained weights into the model
        self.model.load_state_dict(torch.load('final_weight.pth'))

    def test(self, image: torch.Tensor) -> tuple:
        """
        Tests a given image using the loaded model and returns the predictions.

        :param image: The input image tensor.
        :return: A tuple containing predicted class and the output logits from the model.
        """
        # Set CuDNN benchmark and deterministic settings for consistent behavior
        torch.backends.cudnn.benchmark = False

        # Ensure no gradients are computed during testing for efficiency
        with torch.no_grad():
            # Set the model to evaluation mode
            self.model.eval()

            # Move the input image to the appropriate device and compute the output
            inputs = image.to(self.device, non_blocking=True)
            outputs = self.model(inputs)

            # Get the predicted class from the outputs
            pred = outputs.argmax(dim=1, keepdim=True)

            # Return the predicted class and the output logits
            return pred, outputs