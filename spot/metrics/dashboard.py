# Project: spot
# File   : dashboard.py
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

import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from spot.metrics.completion_rate import CompletionRateMetric
from spot.metrics.time_to_solution import TimeToSolutionMetric
from spot.metrics.workload_balance import WorkloadBalanceMetric
from spot.metrics.image_quality import ImageQualityMetric
from spot.metrics.maneuver_duration import ManeuverDurationMetric
from spot.metrics.overlap_complexity import OverlapComplexityMetric


class MetricsDashboard:
    """
    """
    def __init__(self):
        """
        """
        self.time_to_solution = TimeToSolutionMetric()
        self.completion_rate = CompletionRateMetric()
        self.workload_balance = WorkloadBalanceMetric()
        self.image_quality = ImageQualityMetric()
        self.maneuver_duration = ManeuverDurationMetric()
        self.overlap_complexity = OverlapComplexityMetric()

        self.metrics = [ self.completion_rate,
                         self.time_to_solution,
                         self.workload_balance,
                         self.image_quality,
                         self.maneuver_duration,
                         self.overlap_complexity]

        self.build_figure()

    def build_figure(self):
        """
        """
        self.fig = make_subplots(
                rows=6,
                cols=1,
                subplot_titles=([m.name for m in self.metrics])
                )

    def start_recording(self):
        """
        """
        self.time_to_solution.start_recording()
        self.image_quality.start_recording()
        self.maneuver_duration.start_recording()

    def save(self, prefix="mis"):
        """
        """
        for metric in self.metrics:
            np.savetxt(f"{prefix}_{metric.name}.txt", metric.data)

    def update(self, prefix="dashboard"):
        """
        """
        np.savetxt(prefix+"_maneuver_duration.txt", self.maneuver_duration.score)
        np.savetxt(prefix+"_image_quality.txt", self.image_quality.score)
        for metric_id, metric in enumerate(self.metrics):
            if metric.is_scalar:
                self.fig.add_trace(
                        go.Histogram(
                            x=[metric.data],
                            name=metric.name),
                        row=1+metric_id,
                        col=1)

        self.fig.update_layout(
            height=600, width=900,
            title_text="Metrics dashboard"
        )
        self.fig.write_html("metrics_dashboard.html")
