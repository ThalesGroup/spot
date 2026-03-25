# File   : solver_networkx.py
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
import pickle


from spot.rl.environments.satellite import SatelliteEnvironment
from spot.mis.networkx import NetworkXSolver


def solve(requests, satellites, delta_t):
    """ Solves the problem by using the Maximum Independent Set with Networkx
        building solver
    """

    priorities = np.ones(len(requests))

    # read DTOs
    dtos = []
    for satellite_id, _ in enumerate(satellites):
        dto = np.genfromtxt(f"data/dtos_{len(requests)}_{satellite_id+1}.txt", delimiter=" ")
        dtos.append(dto)
    
    # prepare solver
    solver_params={
        "prefix": f"nx_{delta_t}_{len(requests)}_{len(satellites)}",
        "delta_t": delta_t,
    }
    
    solver = NetworkXSolver(solver_params)
    # run solver
    solver.run(
        dtos,
        requests,
        priorities,
        satellites,
        save_graphs=True,
        plot_graphs=True),


if __name__ == "__main__":

    num_requests = 500
    delta_t = 20

    # ISS station
    tle_string = ["1 25544U 98067A   17314.40254821  .00006490  00000-0  10525-3 0 9997",
                  "2 25544  51.6429  29.4166 0004559 104.3372 354.3186 15.54111847 84492"]

    # load satellites
    satellites = []
    for satellite_id in [1, 2, 3]:
        satellite = SatelliteEnvironment(satellite_id)
        satellite.init_from_tle(tle_string)
        satellites.append(satellite)

    # read requests
    requests = np.genfromtxt(f"data/requests_{num_requests}.txt")

    # solve problem
    solve(requests, satellites, delta_t)
