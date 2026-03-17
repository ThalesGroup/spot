# Project: spot
# File   : qubo.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json

from spot.mis.rydberg.solver import RydbergSolver

import qoolqit
from pulser.devices import AnalogDevice
from pulser_pasqal.backends import EmuMPSBackend
from mis import MISInstance, MISSolution
from mis import MISSolver, MISInstance, BackendConfig, BackendType
from qubosolver.config import SolverConfig, PasqalCloud, QPU, RemoteEmulator
from qubosolver import QUBOInstance
from qubosolver.solver import QuboSolver


class SpotQuboSolver(RydbergSolver):
    """
    """
    def __init__(self,params):
        """
        """
        super().__init__(params)

    def extract_maximum_independent_set(self, results, graph):
        """
        """
        pos = nx.get_node_attributes(graph, "pos")

        solving_mis = []

        for node_id, node_value in enumerate(pos.values()):
            print(node_id, node_value)
            if node_id in results:
                solving_mis.append(node_value)
        return solving_mis

    def get_maximum_independent_set(
        self,
        graph,
        subgraph_id=0):
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
                backend= self.get_backend(),
                device= self.get_device(),
            )
        solver = QuboSolver(qubo_mis, qubo_config)

        solution = solver.solve()

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
        
        with open(f"{self.prefix}_qubo_{subgraph_id}.json", 'w') as f:
            json.dump(qubo_results, f)

        return solving_mis
