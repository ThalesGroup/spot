# Project: spot
# File   : image_quality.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025
#
# Copyright 2024 Thales
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
