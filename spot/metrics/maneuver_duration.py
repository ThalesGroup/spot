# Project: spot
# File   : maneuver_duration.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import numpy as np 
import pandas as pd

from .metric import Metric


class ManeuverDurationMetric(Metric):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()
        self.name = "maneuver_duration"
        self.is_scalar = True

    def start_recording(self):
        """
        """
        self.score = []
        
    def add_score(self, maneuver_duration):
        """
        """
        self.score.append(maneuver_duration)

    def compute(self):
        """
        """
        self.data = np.mean(self.score)
