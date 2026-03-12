# Project: spot
# File   : image_quality.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import numpy as np

from .metric import Metric


class ImageQualityMetric(Metric):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()
        self.name = "image_quality"
        self.is_scalar = True

    def start_recording(self):
        """
        """
        self.score = []

    def add_score(self, pitch_distance):
        """
        """
        self.score.append(pitch_distance)

    def compute(self):
        """
        """
        self.data = np.mean(self.score)
