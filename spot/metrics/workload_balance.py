# Project: spot
# File   : workload_balance.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

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
