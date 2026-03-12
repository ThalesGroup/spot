# Project: spot
# File   : overlap_complexity.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import numpy as np
from .metric import Metric


class OverlapComplexityMetric(Metric):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()
        self.name = "overlap_complexity"
        self.is_scalar = True
        self.data = 0

    def compute(self, dtos, start_time=0, end_time=60*60*24):
        """ Computes complexity index in minutes
        """
        return # TODO too long to run, try something smarter
        complexity_index = 0
        min_dates = 0
        max_dates = 60*60*24

        discretizing_arrays = []
        discretizing_array = np.zeros(max_dates)
        for satellith_id, sat_dtos in enumerate(dtos):
            for request_id, dto  in enumerate(sat_dtos):
                dto_start = dto[0]
                dto_end = dto[1]
                for i in range(int(dto_start), int(dto_end)):
                    discretizing_array[i] += 1
            discretizing_arrays.append(discretizing_arrays)

        da = discretizing_arrays[0]
        for i, da_next in enumerate(discretizing_arrays[1:]):
            da += i*da_next

        self.data = np.sum(da)/(end_time-start_time)
