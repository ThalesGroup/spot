# Project: spot
# File   : pulse.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

from spot.mis.rydberg.solver import RydbergSolver
from spot.mis.rydberg.plot import RydbergPlotter
from spot.mis.rydberg.embeddings.autoencoder import AutoencoderEmbedding

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json

from pulser import Pulse, Sequence
from pulser_simulation import QutipEmulator
from pulser.devices import MockDevice
from pulser.waveforms import InterpolatedWaveform


class PulseSolver(RydbergSolver):
    """ PulseSolver
    """
    def __init__(self, params):
        """ initializer
        """
        super().__init__(params=params)
        self.seq = None
        self.has_local_detuning = False
        plt.ioff()

    def prepare_atoms_spatially(self, graph, prefix):
        """ Prepares atoms' spatial layout 
        """
        self.embedder = AutoencoderEmbedding(2)
        self.embedder.compute_embedding(graph, prefix)

    def schedule_pulses(self, graph):
        """ Schedules pulses
        """
        self.target_amplitude = 15
        initial_detuning = -40
        final_detuning = - initial_detuning
        self.pulse_duration = 16000
        
        trap_ids = {v for v in self.embedder.traps}
        reg = self.embedder.layout.define_register(*trap_ids)

        self.seq = Sequence(reg, self.get_device())
        
        # global pulse
        adiabatic_pulse = Pulse(
            InterpolatedWaveform(
                self.pulse_duration,
                [1e-9, self.target_amplitude, 1e-9]),
            InterpolatedWaveform(
                self.pulse_duration,
                [initial_detuning, 0, final_detuning]),
            0,
        )
        self.seq.declare_channel("ising", "rydberg_global")
        self.seq.add(adiabatic_pulse, "ising")

        # use local detuning if graph is weighted
        # to take account for priorities

        if nx.is_weighted(graph) and self.has_local_detuning:
           for node in graph:

               weight = nx.get_node_attributes(node, "weight")

               # priorities are  always positive
               local_detuning = - weight 

               channel_name = f"local_detuning_{node_id}"
               self.seq.declare_channel(name,
                                        "rydberg_local",
                                        initial_target=targets)
               local_pulse = Pulse(
                   InterpolatedWaveform(T, [1e-9, 1E-9, 1e-9]),
                   InterpolatedWaveform(T, [local_detuning/2, 0, -local_detuning/2]),
                   0,
               )
               self.seq.add(local_pulse,
                       name,
                       protocol="no-delay")
            
    def run_simulation(self):
        """
        """
        backend = self.get_backend(self.seq)

        try:
            results = backend.run()
        except:
            print("Warning: graph skipped because qutip cannot solve.")
            return None

        count_dict = results.final_bitstrings

        return count_dict
       
    def extract_maximum_independent_set(self, probs, graph):
        """
        """
        print(probs)
        if probs is None or len(probs) ==0:
            return [], []

        max_keys = [key for key, value in probs.items() \
                if value == max(probs.values())]
        mask = [1 if s=="1" else 0 for s in max_keys[0]]

        if len(mask)==0:
            return [], []

        solving_mis = []
        integer_mis = []

        pos = nx.get_node_attributes(graph, "pos")

        for node_id, node_value in enumerate(pos.values()):
            if node_id>=len(mask):
                continue
            if mask[node_id] == 1:
                solving_mis.append(node_value)
                integer_mis.append(node_id)

        print(solving_mis)
        return solving_mis, integer_mis

    def get_maximum_independent_set(
        self,
        graph,
        subgraph_id=0,
        plot_embedding=True,
        plot_mis=True):
        """
        """
        # compute embedding
        self.prepare_atoms_spatially(
                graph,
                f"{self.prefix}_{subgraph_id}")

        if plot_embedding or plot_mis:
            plotter = RydbergPlotter(self.embedder)

        embedded_graph = self.embedder.embedded_graph

        # save embedding
        if plot_embedding:
            plotter.plot_layout(
                    embedded_graph,
                    file_name=f"{self.prefix}_{subgraph_id}_embedding.png")

        # schedule pulse with embedded register
        self.schedule_pulses(embedded_graph)

        # if number of nodes is not preserved after embedding, skip graph
        if len(embedded_graph.nodes()) != len(graph.nodes()):
            print("Could not find embedding")
            return []

        # run simulation
        try:
            counts = self.run_simulation()
        except:
            return []

        # retrieve Maximum Independent Set with 2 notations:
        # -> solving_label_mis: for solver to retrive final configuratinos
        # -> integer_mis: flattenend qubit ids to integers
        solving_label_mis, integer_mis = \
                self.extract_maximum_independent_set(counts, graph)

        # plot final configuration of atoms with MIS
        if plot_mis:
            plotter.plot_layout(
                    embedded_graph,
                    file_name=f"{self.prefix}_{subgraph_id}_sampled_mis.png",
                    mis_ids=integer_mis)
        pulse_results = {}
        pulse_results["nodes"] = solving_label_mis

        with open(f"{self.prefix}_pulse_{subgraph_id}.json", 'w') as f:
            json.dump(pulse_results, f)

        return solving_label_mis
