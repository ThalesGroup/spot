# Project: spot
# File   : time_to_solution.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

from datetime import datetime

from .metric import Metric


class TimeToSolutionMetric(Metric):
    """
    """
    def __init__(self):
        super().__init__()
        self.name = "time_to_solution"
        self.is_scalar = True

    def start_recording(self):
        """
        """
        self.start = datetime.now()

    def stop(self):
        """
        """
        self.stop = datetime.now()

    def reset(self):
        """
        """
        self.start = 0
        self.end = 0

    def compute(self):
        """
        """
        self.stop()
        self.data = (self.stop - self.start).total_seconds()
        self.reset()
