# File   : compute_dtos.py
# Project: spot
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 22.03.2026
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

from spot.rl.environments.satellite import SatelliteEnvironment


def prepare_satellite(satellite_id):
    """
    """
    # generate satellite and initialize it with a shifted date
    shift_day = satellite_id
    satellite = SatelliteEnvironment(shift_day)
    
    # ISS station
    tle_string = ["1 25544U 98067A   17314.40254821  .00006490  00000-0  10525-3 0 9997",
                  "2 25544  51.6429  29.4166 0004559 104.3372 354.3186 15.54111847 84492"]
    
    # compute ephemeris
    satellite.init_from_tle(tle_string)
    
    return satellite

if __name__ == "__main__":

    for num_requests in [1000]:
        requests = np.genfromtxt(f"data/requests_{num_requests}.txt")
        for satellite_id in [1, 2, 3, 4, 5]:
            print(satellite_id)
            satellite = prepare_satellite(satellite_id)
            dtos = satellite.compute_data_take_opportunity(requests)
            np.savetxt(f"data/dtos_{num_requests}_{satellite_id}.txt", dtos)
