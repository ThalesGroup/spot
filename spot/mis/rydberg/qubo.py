# Project: spot
# File   : qubo.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025
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
import matplotlib.pyplot as plt
import networkx as nx
import json

import qoolqit
from mis import MISInstance, MISSolution
from qubosolver.config import SolverConfig
from qubosolver import QUBOInstance
from qubosolver.solver import QuboSolver

from spot.mis.rydberg.solver import RydbergSolver

class SpotQuboSolver(RydbergSolver):
    """
    """
    def __init__(self,params):
        """
        """
        super().__init__(params)

    def plot_embedding(self, register, file_name="qubo_embedding.png"):
        """
        """
        fig, ax = plt.subplots(1,1)
        register.draw()
        plt.savefig(file_name, dpi=300)

    def extract_maximum_independent_set(self, results, graph):
        """
        """
        pos = nx.get_node_attributes(graph, "pos")

        solving_mis = []

        for node_id, node_value in enumerate(pos.values()):
            if node_id in results:
                solving_mis.append(node_value)
        return solving_mis

    def get_maximum_independent_set(
        self,
        graph,
        subgraph_id=0,
        plot_embedding=True):
        """ 
        """
        instance = MISInstance(graph)
        qubo_mis = QUBOInstance(instance.to_qubo(penalty=None))

        if self.backend_type =="local_emulator":
            qubo_config=SolverConfig(
                use_quantum=True
            )
        elif self.backend_type == "emu_mps_remote_emulator" or  \
             self.backend_type == "fresnel_can1":
            qubo_config = SolverConfig(
                use_quantum=True,
                backend= self.get_qubo_backend(),
                device= self.get_qubo_device(),
            )
        solver = QuboSolver(qubo_mis, qubo_config)

        solution = solver.solve()

        if plot_embedding:
            register = solver.embedding()

            self.plot_embedding(
                register,
                f"{self.prefix}_{subgraph_id}_qubo_embedding.png")

        bitstrings_to_nodes = [
            row.nonzero(as_tuple=True)[0].tolist() \
            for row in solution.bitstrings if row.sum().item() > 0]
    
        # take only the first solution
        mis_sol = MISSolution(
            instance,
            frequency=solution.probabilities[0],
            nodes=bitstrings_to_nodes[0])

        solving_mis = self.extract_maximum_independent_set(
                mis_sol.nodes,
                graph)

        # save results
        qubo_results = {}
        qubo_results["nodes"] = solving_mis
        
        with open(f"{self.prefix}_{subgraph_id}_qubo.json", 'w') as f:
            json.dump(
                qubo_results,
                f,
                indent=4,
                sort_keys=True)

        return solving_mis
