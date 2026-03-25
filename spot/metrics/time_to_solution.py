# Project: spot
# File   : time_to_solution.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025
#
# Copyright 2025 Thales
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
