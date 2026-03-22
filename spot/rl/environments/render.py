# Project: spot
# File   : render.py
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
import pandas as pd
import math

import plotly.express as px
import plotly.graph_objects as go


class RenderEngine:
    """
    """
    def __init__(self, requests, satellites):

        self.requests = requests
        self.reset_satellites(satellites)

    def reset_satellites(self, satellites):
        """
        """
        alts=[]
        times=[]
        frames=[]

        self.colors = [
        "lightgreen",
        "#90D5FF", 
        "#FFBF00",
        ]

        los = []
        las = []
        for satelilte_id, satellite in enumerate(satellites):
            positions = satellite.positions

            lats=[]
            lons=[]

            for time, position in enumerate(positions[1:-1]):
                if time % 60!= 0:
                    continue 
                lon = position[0]
                lat = position[1]

                lons.append(lon)
                lats.append(lat)
                times.append(time)
            los.append(lons)
            las.append(lats)

        self.lons = los
        self.lats = las
        self.times = times
        self.satellites = satellites

    def render_requests(self):
        """
        """
        fig=go.Scattergeo(
                lat=self.requests[:,1],
                lon=self.requests[:,0],
                mode="markers",
                # line=dict(width=2, color="gray"),
                marker=dict(color="yellow",
                    opacity=1,
                    size=12,
                    line=dict(
                        color='black',
                        width=4
                        )
                    # symbol="square"
                    ),
                visible="legendonly",
                geo="geo"
                )
        return fig

    def render_satellites(self):
        """
        """
        figs = []
        for satellite_id, satellite in enumerate(self.satellites):

            figs.append(go.Scattergeo(
                lat=self.lats[satellite_id],
                lon=self.lons[satellite_id],
                mode="lines",
                line=dict(width=2, color=self.colors[satellite_id]),
                # showlegend=False,
                visible="legendonly",
                geo="geo"
                ))
        return figs

    def render(self):
        """
        """
        fig = go.Figure(
                go.Scattergeo(),
                )
        lyt = dict(
                map_style="outdoors",
                width=1920/1.3,
                height=1080/1.3,
                plot_bgcolor="#171b26",
                paper_bgcolor="#171b26",
                geo = dict(
                    resolution=110,
                    showland=True,
                    showocean=True,
                    showcountries=True,
                    oceancolor="#064273",
                    projection = dict(scale=1),
                    )
                )

        fig.update_layout(lyt)

        fig_requests = self.render_requests()
        fig_satellites = self.render_satellites()

        fig.add_traces(fig_requests)

        for fig_sat in fig_satellites:
            fig.add_traces(fig_sat)

        fig.update_layout(
                 autosize=True,
                 hovermode='closest',
                 map=dict(
                     bearing=0,
                     pitch=0,
                     zoom=0.1
                 ),
            )
        fig.write_html("satellites.html")

        return fig
