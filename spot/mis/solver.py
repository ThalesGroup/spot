# Project: spot
# File   : solver.py
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
import time
import math
import json
import networkx as nx
from datetime import datetime, timedelta
import pickle
import random

import orekit
orekit.initVM()
from org.orekit.bodies import GeodeticPoint

from spot.mis.postprocessing import Postprocessor
from spot.metrics.dashboard import MetricsDashboard
from spot.rl.environments.utils import datetime_to_absolutedate

class CollectOpportunity:
    """
    """
    def __init__(self,
                 start_time,
                 end_time,
                 start_attitude,
                 end_attitude,
                 satellite_id,
                 request_id):
        """
        """
        self.start_time = int(start_time)
        self.end_time = int(end_time)
        self.start_attitude = start_attitude
        self.end_attitude = end_attitude
        self.satellite_id = satellite_id
        self.request_id = request_id
        
class Solver():
    """ Solver base class
        """
    def __init__(self, params=None):
        """ Initializer
        """
        self.delta_t=120
        self.dt = 1
        self.prefix = "solver"
        if params:
            self.prefix = params.get("prefix", "solver")
            self.delta_t= params.get("delta_t", self.delta_t)

    def get_attitude(self, satellite, t, request_position):
        """
        """
        requested_date =  datetime_to_absolutedate(
            satellite.initial_date + timedelta(seconds=t))

        requested_target = GeodeticPoint(
                math.radians(request_position[0]/180*np.pi),
                math.radians(request_position[1]/180*np.pi),
                math.radians(0.));

        requested_attitude = satellite.pointing_to_attitude(
            requested_date,
            requested_target)

        return requested_attitude

    def get_agility_constraint(
        self,
        collect_opportunity1,
        collect_opportunity2):
        """
        """
        satellite_id1 = collect_opportunity1.satellite_id
        satellite_id2 = collect_opportunity2.satellite_id

        satellite_id = satellite_id1
        satellite = self.satellites[satellite_id]

        start_time = collect_opportunity2.start_time
        end_time = collect_opportunity1.end_time

        start_attitude = collect_opportunity2.start_attitude
        end_attitude = collect_opportunity1.end_attitude

        maneuver_duration = satellite.get_maneuver_duration(
            end_attitude,
            start_attitude)

        acquisition_date =\
            satellite.initial_date +\
            timedelta(seconds=start_time) +\
                              timedelta(seconds=maneuver_duration)

        # distance on ground of target
        target_distance = 100

        acquisition_duration = satellite.get_acquisition_duration(
                target_distance,
                datetime_to_absolutedate(acquisition_date),
                requested_target)

        if maneuver_duration + acquisition_duration <= start_time - end_time:
            return True
        else:
            return False
        

    def get_repetition_constraint(
        self,
        collect_opportunity1,
        collect_opportunity2):
        """
        """
        request_id1 = collect_opportunity1.request_id
        request_id2 = collect_opportunity2.request_id

        if request_id1 != request_id2:
            return True
        else:
            return False

    def get_satellite_constraint(
        self,
        collect_opportunity1,
        collect_opportunity2):
        """
        """
        satellite_id1 = collect_opportunity1.satellite_id
        satellite_id2 = collect_opportunity2.satellite_id

        if satellite_id1 != satellite_id2:
            return True
        else:
            return False

    def collect_opportunities(self,
                        dtos,
                        priorities,
                        begin=True,
                        discretizing_array=None):
        """ Discretizes Data Take Opportunities into time steps according to a
        given strategy. If discretizing_array is provided, it is used for
        splitting. Otherwise, a uniform discretization is applied based on the
        minimum acquisistion duration delta_t

        Arguments:
            dtos: list of Data Take Opportunities
            priorities : list of priorities for requests
        """
        collected_opportunities= []

        for satellite_id, sat_dtos in enumerate(dtos):

            satellite = self.satellites[satellite_id]

            sampled_opportunities = []
            request_opportunities= []
            for request_id, (dto, priority) in\
                enumerate(zip(sat_dtos, priorities)):

                self.dto_start = dto[0]
                self.dto_end = dto[1]
                if self.dto_start<=0:
                    continue
                t = 0
                while t < 60*60*24:
                    if t >= self.dto_start and t <= self.dto_end:

                        start_time = t
                        end_time = self.dto_end

                        request_position = self.requests_positions[request_id]

                        start_attitude = self.get_attitude(
                            self.satellites[satellite_id],
                            start_time,
                            request_position)

                        end_attitude = self.get_attitude(
                            self.satellites[satellite_id],
                            end_time,
                            request_position)

                        collect_opportunity = CollectOpportunity(
                            t,
                            end_time,
                            start_attitude,
                            end_attitude,
                            satellite_id,
                            request_id,
                        )
                        collected_opportunities.append(collect_opportunity)
                    t += self.delta_t

        return collected_opportunities

    def graph_from_collect_opportunities(
        self,
        collected_opportunities,
        priorities,
        method="edges"):
        """ Generates a graph from discretized Data Take Opportunities
        """
        graph = nx.Graph()

        for index, op in enumerate(collected_opportunities):
            graph.add_node(
                index,
                pos=(op.request_id, op.start_time, op.satellite_id))
                
        for index1, op1 in enumerate(collected_opportunities):
            for index2, op2 in enumerate(collected_opportunities):
                if index2 == index1:
                    continue
                r1 = op1.request_id
                r2 = op2.request_id

                t1 = op1.start_time
                t2 = op2.start_time

                s1 = op1.satellite_id
                s2 = op2.satellite_id

                if method =="edges":
                    if t1==t2 and s1==s2:
                        graph.add_edge(index1, index2)

                    if r1==r2:
                        graph.add_edge(index1, index2)
                elif method=="constraints":

                    agility_constraint = self.get_agility_constraint(op1, op2)
                    repetition_constraint= self.get_repetition_constraint(op1, op2)
                    multi_satellite_constraint = self.get_satellite_constraint(op1, op2)

                    if self.num_satellites > 1:
                        if not agility_constraint and \
                           not repetition_constraint and \
                           not multi_satellite_constraint:
                            graph.add_edge(index1, index2)
                    else:
                        if not agility_constraint and \
                           not repetition_constraint:
                            graph.add_edge(index1, index2)
        return graph

    def merge_local_solutions(self, start_local_solutions):
        """ Merges local solutions to a global plan
        """

        global_plan = {}

        for start_node in start_local_solutions:
            request_id = start_node[0]
            begin_time_step = start_node[1]
            satellite_id = start_node[2]
            if request_id not in global_plan.keys():
                global_plan[request_id] = (satellite_id, begin_time_step)

        return global_plan
        
    def save_graph(self, graph_id, graph):
        """
        """
        with open(f"{self.prefix}_subgraph_{graph_id}.nx", 'wb') as file:
            pickle.dump(graph, file)

    def run(self,
            dtos,
            requests,
            priorities,
            satellites,
            greedy=True,
            save_graphs=False,
            plot_graphs=False):
        """ Run
        """
        self.dashboard = MetricsDashboard()
        self.dashboard.start_recording()
        self.dashboard.overlap_complexity.compute(dtos)

        self.satellites = satellites
        self.priorities = priorities
        self.num_satellites = len(satellites)
        self.num_requests = len(requests)
        self.requests_positions = requests

        # discretize data take opportunities
        collect_opportunities=\
            self.collect_opportunities( \
                dtos,
                priorities)

        graph = self.graph_from_collect_opportunities(
            collect_opportunities,
            priorities)

        if save_graphs:
            self.save_graph("total", graph)
    
        if plot_graphs:
            postprocessor = Postprocessor(
                self.num_satellites,
                self.num_requests)
            postprocessor.plot_graph(graph, prefix=f"{self.prefix}_total")


        # prepare MIS
        mis = []
        subgraphs_stats = {}

        pos = nx.get_node_attributes(graph, "pos")

        subgraphs = [graph.subgraph(c) for c in nx.connected_components(graph)]

        for graph_id, subgraph in enumerate(subgraphs):
            subgraph_len = subgraph.number_of_nodes()

            if subgraph_len <= 2:
                for node in subgraph.nodes():
                    mis += [pos.get(node)]
                    break
                continue

            start_time = datetime.now()

            mis += self.get_maximum_independent_set(
                subgraph,
                subgraph_id=graph_id)

            end_time = datetime.now()
            elapsed_time = end_time - start_time

            subgraphs_stats[graph_id] = {
                "num_nodes": subgraph_len,
                "num_edges": len(subgraph.edges),
                "elapsed_time": elapsed_time.microseconds
                }

            if save_graphs:
                self.save_graph(graph_id, subgraph)

            if plot_graphs:
                postprocessor = Postprocessor(
                    self.num_satellites,
                    self.num_requests)

                postprocessor.plot_graph(
                    subgraph,
                    prefix=f"{self.prefix}_{graph_id}")

        global_plan = self.merge_local_solutions(mis)

        self.dashboard.time_to_solution.compute()
        self.dashboard.maneuver_duration.compute()
        self.dashboard.image_quality.compute()
        self.dashboard.completion_rate.compute(
                graph,
                priorities,
                global_plan)
        self.dashboard.workload_balance.compute(
                self.num_satellites,
                self.num_requests,
                global_plan)

        results = {}
        for metric in self.dashboard.metrics:
            results[f"{metric.name}"] = metric.data

        results["global_plan"] = global_plan
        results["subgraphs"] = subgraphs_stats

        with open(f'{self.prefix}_result.json', 'w') as f:
            json.dump(
                results,
                f,
                indent=4,
                sort_keys=True)

        return graph, results
