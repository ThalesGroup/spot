# Project: spot
# File   : unit_disk.py
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

import numpy as np
import networkx as nx

from pulser.devices import MockDevice
from scipy.constants import hbar

from sklearn.preprocessing import MinMaxScaler

import matplotlib.pylab as plt

from pulser.register.special_layouts import TriangularLatticeLayout

from scipy.spatial import distance

import json

class UnitDiskEmbedding:
    """ Base class for unit disk embedding
    """
    def __init__(self, layout_dim, device=None):
        """ initializer
        """
        # layout
        self.layout_dim = layout_dim

        self.num_traps = 61
        self.spacing = 5.
        self.blockade_radius = 7.
        self.tolerance = 1E-1
        self.layout = device

        print("MIN LAYOUT FILLING", device.min_layout_filling)
        if device is None:
            self.layout = TriangularLatticeLayout(
                    n_traps=self.num_traps,
                    spacing=self.spacing)
        else:
            self.layout = device.calibrated_register_layouts[
                "TriangularLatticeLayout(61, 5.0µm)"]


    def squared_distance(self, i, j):
        """ Compute the squared distance between atoms
        """
        if self.layout_dim == 2:
            return ((self.get_positions(i)[0] - self.get_positions(j)[0])**2 + \
                    (self.get_positions(i)[1] - self.get_positions(j)[1])**2) 
        elif self.layout_dim == 3:
            return ((self.get_positions(i)[0] - self.get_positions(j)[0])**2 + \
                    (self.get_positions(i)[1] - self.get_positions(j)[1])**2 + \
                    (self.get_positions(i)[2] - self.get_positions(j)[2])**2) 


    def preprocess_graph(self, graph):
        """ Performs spring layout preprocessing and rescaling for initial guess
        """
        # ease work with spring layout
        initial_layout = nx.spring_layout(graph)
        initial_layout = [a for a in initial_layout.values()]

        # scales to fit standard grid of 100x100 micro meters
        scaler = MinMaxScaler(feature_range=(-50, 50))
        self.initial_layout = scaler.fit_transform(initial_layout)

        # store graph properties
        self.num_nodes = len(graph.nodes())

        return graph

    def dump_results(self):
        """
        """
        results = {}
        results["optimized_layout"] = self.optimized_layout
        results["traps_coords"] = self.layout._coords
        results["qubit_trap_id"] = self.traps

        with open(self.prefix+"_unit_disk_embedder.json", 'w') as f:
            json.dump(
                    results,
                    f,
                    indent=4,
                    sort_keys=True)

    def get_embedded_graph(self):
        """
        """
        # retrieve embedded_graph
        embedded_graph = nx.Graph()

        for node_id in range(self.num_nodes):
            embedded_graph.add_node(
                    node_id,
                    pos=self.layout._coords[self.traps[node_id]])

        pos = nx.get_node_attributes(embedded_graph, "pos")

        for node_i in embedded_graph.nodes():
            pos_i = pos[node_i]

            for node_j in embedded_graph.nodes():
                if node_i == node_j:
                    continue
                pos_j = pos[node_j]

                if distance.euclidean(pos_i, pos_j) <= \
                        self.blockade_radius:
                    embedded_graph.add_edge(node_i, node_j)

        return embedded_graph

    def compute_embedding(self, graph, prefix):
        """
        """
        # store prefix for output
        self.prefix = prefix

        # preprocess graph
        preprocessed_graph = self.preprocess_graph(graph)

        # run the core algorithm
        self.embedded_graph = self.run(preprocessed_graph)

        self.dump_results()

        return self.embedded_graph
