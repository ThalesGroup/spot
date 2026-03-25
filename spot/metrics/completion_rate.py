# Project: spot
# File   : completion_rate.py
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
import networkx as nx

from .metric import Metric


class CompletionRateMetric(Metric):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()
        self.name = "completion_rate"
        self.is_scalar = True

    def compute(self, graph, priorities, global_plan):
        """ Compute completion rates
        """
        # retrieve completed requests list
        completed_requests = np.zeros((len(priorities),1))
        pos = nx.get_node_attributes(graph, "id")

        for request_id in global_plan.keys():
            completed_requests[int(request_id)] = 1

        # compute global completion rates
        global_completion_rate = np.mean(completed_requests)*100

        # compute priorized completion rates
        prioritized_completion_rates = {}
        for priority_level in np.unique(priorities):
            prioritized_completion_rates[priority_level] = \
                np.mean(completed_requests[np.where(priorities==priority_level)])*100

        self.data = {
            "global_completion_rate": global_completion_rate,
            "prioritized_completion_rates": prioritized_completion_rates,
        }
