# File   : sample_requests.py
# Project: spot
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 22.03.2026
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
import pandas


def sample_requests(requests, num_requests):
    """
    """
    # random cities
    vals = np.array(requests.sample(num_requests).values,dtype="float")
    lrequests = np.flip(vals,axis=1)
    np.savetxt(f"data/requests_{num_requests}.txt", lrequests)


if __name__ == "__main__":

    requests = pandas.read_csv("data/worldcities.csv", sep=",",usecols=["lat","lng"])

    for num_requests in [10, 50, 100, 500, 1000]:
        sample_requests(requests, num_requests)
