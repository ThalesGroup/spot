# Project: spot
# File   : pulse.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

from spot.mis.solver import Solver
from spot.mis.rydberg.plot import RydbergPlotter
from spot.mis.rydberg.embeddings.autoencoder import AutoencoderEmbedding

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle

from pulser import Pulse, Sequence
from pulser_simulation import QutipEmulator
from pulser.devices import MockDevice
from pulser.waveforms import InterpolatedWaveform


class PulseSolver(Solver):
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

        self.seq = Sequence(reg, MockDevice)
        
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
        simul = QutipEmulator.from_sequence(self.seq, sampling_rate=1)

        try:
            results = simul.run()
        except:
            print("Warning: graph skipped because qutip cannot solve.")
            return None

        final = results.get_final_state()
        count_dict = results.sample_final_state()

        return count_dict
       
    def extract_maximum_independent_set(self, probs, graph):
        """
        """
        if probs is None or len(probs) ==0:
            return [], []

        max_keys = [key for key, value in probs.items() \
                if value == max(probs.values())]
        mask = [1 if s=="1" else 0 for s in max_keys[0]]

        if len(mask)==0:
            return [], []

        mis = []
        integer_mis = []

        for node_id, (_, node_value) in \
                enumerate(dict(graph.nodes(data="solving_label")).items()):
            if node_id>=len(mask):
                continue
            if mask[node_id] == 1:
                mis.append(node_value)
                integer_mis.append(node_id)

        return mis, integer_mis

    def get_maximum_independent_set(
        self,
        graph,
        plot_embedding=False,
        plot_mis=False,
        suffix=""):
        """
        """
        if plot_embedding or plot_mis:
            plotter = RydbergPlotter(self.embedder)

        # compute embedding
        self.prepare_atoms_spatially(
                graph,
                f"{self.prefix}_{suffix}")

        embedded_graph = self.embedder.embedded_graph

        # save embedding
        if plot_embedder:
            plotter.plot_layout(
                    embedded_graph,
                    file_name=f"{self.prefix}_{i}_{num_nodes}_embedding.png")

        # schedule pulse with embedded register
        self.schedule_pulses(embedded_graph)

        # if number of nodes is not preserved after embedding, skip graph
        if len(embedded_graph.nodes()) != len(graph.nodes()):
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

        mis += solving_label_mis

        # plot final configuration of atoms with MIS
        if plot_mis:
            plotter.plot_layout(
                    embedded_graph,
                    file_name=f"{self.prefix}_{i}_sampled_mis.png",
                    mis_ids=integer_mis)

        with open(f"{self.prefix}_graph_{i}.mis", 'wb') as file:
            pickle.dump(mis, file)

        return mis
