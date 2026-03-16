# Project: spot
# File   : qubo.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle

from spot.mis.solver import Solver
from spot.mis.rydberg.cloud import PasqalCloudManager

import qoolqit
from pulser.devices import AnalogDevice
from pulser_pasqal.backends import EmuMPSBackend
from mis import MISInstance, MISSolution
from mis import MISSolver, MISInstance, BackendConfig, BackendType
from qubosolver.config import SolverConfig, PasqalCloud, QPU, RemoteEmulator
from qubosolver import QUBOInstance
from qubosolver.solver import QuboSolver


class SpotQuboSolver(Solver):
    """
    """
    def __init__(self,params):
        """
        """
        super().__init__(params)

    def extract_maximum_independent_set(self, results, graph):
        """
        """
        mis = []
        integer_mis = []

        for node_id, (_, node_value) in \
                enumerate(dict(graph.nodes(data="solving_label")).items()):
            if node_id in results:
                mis.append(node_value)
                integer_mis.append(node_id)

        return mis, integer_mis

    def get_maximum_independent_set(
        self,
        graph,
        suffix=""):
        """ 
        """
        instance = MISInstance(graph)

        manager = PasqalCloudManager()

        connection = PasqalCloud(
            username=manager.username,
            password=manager.password,
            project_id=manager.project_id,
        )

        device = qoolqit.devices.Device(pulser_device=connection.fetch_available_devices()["FRESNEL_CAN1"])
        config = SolverConfig(
            use_quantum=True,
            backend = QPU(connection=connection, runs=100),
            device=device,

        )

        qubo_mis = QUBOInstance(instance.to_qubo(penalty=None))
        solver = QuboSolver(qubo_mis, config)

        solution = solver.solve()

        bitstrings_to_nodes = [row.nonzero(as_tuple=True)[0].tolist() for row in solution.bitstrings if row.sum().item() > 0]
    
        # take only the first solution
        mis_sol = MISSolution(instance, frequency=solution.probabilities[0], nodes=bitstrings_to_nodes[0])

        solving_mis, integer_mis = self.extract_maximum_independent_set(
                mis_sol.nodes,
                graph)

        qubo_results["nodes"] = solving_mis
        
        with open(f"{self.prefix}_qubo_{suffix}_.json", 'w') as f:
            json.dump(qubo_results, f)
        
        print(solving_mis)
        

        return solving_mis
