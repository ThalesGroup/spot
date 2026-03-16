# Project: spot
# File   : autoencoder.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

from .unit_disk import UnitDiskEmbedding


import sys
import numpy as np
import keras
import tensorflow as tf
from keras import layers
import networkx as nx
import matplotlib.pylab as plt

from scipy.spatial import distance


class AutoencoderEmbedding(UnitDiskEmbedding):
    """ Autoencoder model for unit disk embedding of graphs
    """
    def __init__(self, layout_dim):
        """
        """
        super().__init__(layout_dim)
        self.losses = []
    
    def build_model(self):
        """ Build the autoencoder model
        """
        self.model = keras.Sequential(
            [
                layers.Dense(
                    self.num_nodes*self.layout_dim,
                    activation="relu"),
    
                layers.Dense(128,
                    activation="relu",
                    name="layer2"),
    
                layers.Dense(64,
                    activation="relu",
                    name="layer3"),

                layers.Dense(6,
                    activation="relu",
                    name="layer4"),

                layers.Dense(64,
                    activation="relu",
                    name="layer5"),

                layers.Dense(128,
                    activation="relu",
                    name="layer6"),
    
                layers.Dense(
                    self.num_nodes*self.layout_dim,
                    activation="linear",
                    name="output_layer")
            ])

        self.early_stopper_callback = \
                keras.callbacks.EarlyStopping(
                        monitor='loss',
                        patience=200)

    def get_positions(self, node_id):
        """
        """
        output = self.model( \
                self.initial_layout.reshape(1, self.num_nodes*self.layout_dim))
    
        output = tf.reshape(output, (self.num_nodes, self.layout_dim))

        return output[node_id]
    
    def compute_distances(self):
        """ Compute distances of a register containes in self.positions
        """
        distances = []
        for i in self.graph.nodes():
            for j in self.graph.nodes():
                if i<j:
                    distances.append(tf.sqrt(self.squared_distance(i, j)))

        return distances
    
    def attract_loss(self):
        """ 
        """
        return tf.reduce_mean(tf.abs(tf.maximum(100., self.distances) - 100.))
    
    def push_loss(self):
        """ 
        """
        return tf.reduce_mean(tf.abs( \
            tf.minimum(
                self.spacing,
                self.distances) - \
                        self.spacing))
    
    def edge_loss(self):
        """ Computes loss for edges of graph
        """
        return tf.reduce_mean(self.coeffs * tf.abs( \
                tf.maximum(
                    self.blockade_radius,
                    self.distances) - \
                            self.blockade_radius))
    
    def non_edge_loss(self):
        """ Computes loss for complementary edges of graph
        """
        return tf.reduce_mean(
                (tf.ones(np.shape(self.coeffs)) - self.coeffs) *\
                tf.abs( tf.minimum(
                    self.blockade_radius + self.tolerance,
                    self.distances) - \
                    self.blockade_radius -\
                    self.tolerance))
    
    def loss(self, output):
        """ Computes global loss
        """
        self.distances = self.compute_distances()
    
        loss = self.attract_loss() + \
               self.push_loss() + \
               self.edge_loss() + \
               self.non_edge_loss()

        self.losses.append(loss)
    
        return loss
    
    def run(
        self,
        graph,
        save_loss=False,
        plot_loss=False):
        """ Trains the autoencoder
        """
        self.graph = graph

        self.coeffs = []
        for i in self.graph.nodes():
            for j in self.graph.nodes():
                if i<j:
                    if (i,j) in self.graph.edges():
                        self.coeffs.append(1.)
                    else:
                        self.coeffs.append(0.)

        def local_loss(inputs, outputs):
            """ Local wrapper for keras
            """
            return tf.losses.mean_squared_error(inputs, outputs) * (1E-2 + self.loss(outputs))
    
        # build and train model
        self.build_model()
        optimizer = keras.optimizers.Adam(learning_rate=0.01)
        self.model.compile(optimizer, local_loss)
    
        hist = self.model.fit(
                self.initial_layout.reshape(1, self.num_nodes*self.layout_dim),
                self.initial_layout.reshape(1, self.num_nodes*self.layout_dim),
                epochs=500,
                batch_size=1,
                callbacks=[self.early_stopper_callback])

        losses = hist.history["loss"]

        if save_loss:
            np.savetxt(f"{self.prefix}_autoencoder_loss.txt", losses)

        if plot_loss:
            fig, ax = plt.subplots(1, 1)
            ax.plot(losses)
            ax.set_yscale("log")
            ax.set_xlabel("iterations")
            ax.set_ylabel("loss")
            fig.savefig(f"{self.prefix}_autoencoder_loss.png")
    
        # retrieve optimized layout
        output = self.model( \
                self.initial_layout.reshape(1, self.num_nodes*self.layout_dim))
        output = tf.reshape(output, (self.num_nodes, self.layout_dim)).numpy()
    
        self.traps = []
        self.optimized_layout = []
    
        # project on traps
        for node_pos in output:
            dist_to_traps = []
            self.optimized_layout.append([float(node_pos[0]), float(node_pos[1])])

            for trap_id, trap_coords in enumerate(self.layout.coords):
                dist_to_traps.append( distance.euclidean(
                    [float(node_pos[0]), float(node_pos[1])],
                    trap_coords))

            trap_found = np.argmin(dist_to_traps)
            self.traps.append(int(trap_found))

        return self.get_embedded_graph()
