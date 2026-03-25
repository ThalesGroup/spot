# Project: spot
# File   : plot.py
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

import matplotlib.pylab as plt


class RydbergPlotter:
    """
    """
    def __init__(self, embedder):
        """
        """
        self.embedder = embedder

    def plot_layout(self, graph, file_name="layout.png", mis_ids=None):
        """
        """
        fig, ax = plt.subplots(1,1)

        trap_ids = {v for v in self.embedder.traps}
        reg = self.embedder.layout.define_register(*trap_ids)

        if mis_ids is not None:
            colors_mapping = {}

            for qubit_id in range(len(self.embedder.traps)):
                if qubit_id in mis_ids:
                    colors_mapping[f"q{qubit_id}"] = "red"
                else:
                    colors_mapping[f"q{qubit_id}"] = "grey"
            reg.draw(
                blockade_radius= self.embedder.blockade_radius,
                draw_graph=True,
                with_labels=False,
                qubit_colors=colors_mapping,
                show=False,
                custom_ax=ax)
        else:
            reg.draw(
                blockade_radius= self.embedder.blockade_radius,
                draw_half_radius=True,
                draw_graph=True,
                with_labels=False,
                show=False,
                custom_ax=ax
            )

        self.embedder.layout._draw_2D(
                ax,
                self.embedder.layout.coords,
                range(self.embedder.num_traps),
                with_labels=False,
                are_traps=True,
            )

        fig.savefig(file_name, dpi=300)
