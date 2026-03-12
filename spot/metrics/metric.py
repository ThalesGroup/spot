# Project: spot
# File   : metric.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025


class Metric:
    """ Base class for metric
    """
    def __init__(self):
        """
        """
        self.metric_name = "metric"
        self.data = {}

    def init(self):
        """
        """
        raise ValueError("To be implemented in child class")

    def compute(self):
        """
        """
        raise ValueError("To be implemented in child class")
