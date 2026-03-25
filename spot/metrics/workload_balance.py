# Project: spot
# File   : workload_balance.py
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

from .metric import Metric


class WorkloadBalanceMetric(Metric):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()
        self.name = "workload_balance"
        self.is_scalar = False

    def compute(self, num_satellites, num_requests, global_plan):
        """ Compute satellites workloads
        """
        satellites_workload = {}
        for satellite_id in range(num_satellites):
            satellites_workload[satellite_id] = 0

        for satellite_id, begin_time_slot in global_plan.values():
            satellites_workload[satellite_id] += 1/num_requests*100

        self.data = satellites_workload
