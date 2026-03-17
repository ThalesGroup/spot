# Project: spot
# File   : postprocessing.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.2025

import networkx as nx
import matplotlib.pylab as plt 
import matplotlib as mpl


class Postprocessor:
    """
    """
    def __init__(self, num_satellites, num_requests):
        """
        """
        self.num_satellites = num_satellites
        self.num_requests = num_requests

    def plot_graph(self, graph, mis=None, prefix="mis"):
        """
        """
        
        fig, ax = plt.subplots(1,1)
        color_map = []
        node_size_map = []

        vir = mpl.cm.get_cmap("viridis")
        vmin, vmax = 0, self.num_satellites
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

        pos = nx.get_node_attributes(graph, "pos")
        for node_id, node in enumerate(graph):
            pos_values = list(pos.values())
            satellite_id = pos_values[node_id][2]
            if mis is None:
                color_map.append(vir(norm(satellite_id)))
                node_size_map.append(100)
            else:
                if node in mis:
                    color_map.append("red")
                    node_size_map.append(500)
                else:
                    color_map.append(vir(norm(satellite_id)))
                    node_size_map.append(100)

        graph_plot = nx.draw_spring(
                graph,
                node_color=color_map,
                node_size=node_size_map)

        norm = plt.Normalize(vmin=vmin, vmax=vmax)

        sm = plt.cm.ScalarMappable(cmap=vir, norm=norm)
        sm.set_array([])

        satellite_dots = vir(norm(range(self.num_satellites)))
        custom_lines = [mpl.lines.Line2D([0], [0], color=c, lw=2) for c in satellite_dots]
        custom_lines.append(mpl.lines.Line2D([0], [0], color="red",lw=2))
        custom_labels = list(range(self.num_satellites)) + ["MIS"]

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        legend_sats = ax.legend(custom_lines[:-1], custom_labels[:-1],
                title="satellite id", loc="upper left", bbox_to_anchor=(1, 1))
        ax.add_artist(legend_sats)

        if mis is not None:
            ax.legend([custom_lines[-1]], [custom_labels[-1]], title="solution",
                    loc="upper left", bbox_to_anchor=(1, 0.2))

        fig.savefig(prefix+"_graph.png",dpi=300)
        plt.close()
