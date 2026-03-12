# Project: spot
# File   : networkx.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

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
            fixed_nodes=None):
        """
        """
        pos = nx.get_node_attributes(graph, "pos")
        mis = nx.maximal_independent_set(graph)

        solving_mis = []
        for node_id, node_value in enumerate(pos.values()):
            if node_id in mis:
                solving_mis.append(node_value)
        return solving_mis
