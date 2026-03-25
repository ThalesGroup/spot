# Project: spot
# File   : networkx.py
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


import networkx as nx

from spot.mis.solver import Solver


class NetworkXSolver(Solver):
    """
    """
    def __init__(self, params=None):
        """
        """
        super().__init__(params=params)

    def get_maximum_independent_set(
            self,
            graph,
            subgraph_id=0):
        """
        """
        pos = nx.get_node_attributes(graph, "pos")
        mis = nx.maximal_independent_set(graph)

        solving_mis = []
        for node_id, node_value in enumerate(pos.values()):
            if node_id in mis:
                solving_mis.append(node_value)
        return solving_mis
