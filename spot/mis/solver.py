# Project: spot
# File   : solver.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.10.23025

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

from spot.rl.environments.utils import datetime_to_absolutedate
from spot.rl.environments.utils import absolutedate_to_datetime
from spot.mis.distributed_solver import ExactDistributedSolver
from spot.mis.distributed_solver import GreedyDistributedSolver
from spot.mis.distributed_solver import CoreDistributedSolver
from spot.mis.distributed_solver import KaHIPDistributedSolver
from spot.mis.postprocessing import Postprocessor
from spot.metrics.dashboard import MetricsDashboard
from spot.rl.environments.satellite import datetime_to_absolutedate

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
        self.prefix = "solver"
        if params:
            self.prefix = params.get("prefix", "solver")
            self.delta_t= params.get("delta_t", self.delta_t)

    def get_agility_constraint(self, collect_opportunity1, collect_opportunity2):
        """
        """
        satellite_id1 = collect_opportunity1.satellite_id
        satellite_id2 = collect_opportunity2.satellite_id

        satellite_id = satellite_id1
        satellite = self.satellites[satellite_id]

        start_time = collect_opportunity2.start_time
        end_time = collect_opportunity1.end_time

        start_attitude = collect_opportunity1.start_attitude
        end_attitude = collect_opportunity2.end_attitude

        request_id1 = collect_opportunity1.request_id
        request_id2 = collect_opportunity2.request_id

        requested_date =  datetime_to_absolutedate(
            satellite.initial_date + timedelta(seconds=start_time))

        request_position = self.requests_positions[request_id1]

        requested_target = GeodeticPoint(
                math.radians(request_position[0]),
                math.radians(request_position[1]),
                math.radians(0.));

        requested_attitude = self.satellites[satellite_id1].pointing_to_attitude(
            requested_date,
            requested_target)
            
        maneuver_duration = satellite.get_maneuver_duration(
            start_attitude,
            requested_attitude)

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
        

    def get_repetition_constraint(self, collect_opportunity1, collect_opportunity2):
        """
        """
        request_id1 = collect_opportunity1.request_id
        request_id2 = collect_opportunity2.request_id

        if request_id1 != request_id2:
            return True
        else:
            return False

    def get_satellite_constraint(self, collect_opportunity1, collect_opportunity2):
        """
        """
        satellite_id1 = collect_opportunity1.satellite_id
        satellite_id2 = collect_opportunity2.satellite_id

        if satellite_id1 == satellite_id2:
            return True
        else:
            return False

    def discretize_dtos(self,
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
        sampled_collected_opportunities=[]

        if discretizing_array is not None:
            if not isinstance(discretizing_array, np.array):
                raise ValueError("Discretizing array should be np.array.")
        else:
            min_dates = 0
            max_dates = 60*60*24
            discretizing_array = np.linspace(
                    0,
                    max_dates,
                    int(max_dates/self.delta_t))

        for satellite_id, sat_dtos in enumerate(dtos):

            satellite = self.satellites[satellite_id]

            sampled_opportunities = []
            request_opportunities= []
            for i in range(len(discretizing_array)-1):
                for request_id, (dto, priority) in enumerate(zip(sat_dtos, priorities)):
                    dto_start= dto[0]
                    if dto_start<1:
                        continue
                    dto_end = dto[1]
                    if dto_start -40 < discretizing_array[i] and \
                       discretizing_array[i] <= dto_end:

                        collect_opportunity = CollectOpportunity(
                            int(discretizing_array[i]),
                            int(dto_end),
                            [math.radians(0) , math.radians(0), math.radians(0)],
                            [math.radians(0) , math.radians(0), math.radians(0)],
                            satellite_id,
                            request_id,
                        )
                        request_opportunities.append(collect_opportunity)
                        collected_opportunities.append(collect_opportunity)
                sampled_opportunities.append(request_opportunities)
            sampled_collected_opportunities.append(sampled_opportunities)

        return collected_opportunities, sampled_collected_opportunities

    def graph_from_collect_opportunities(
        self,
        collected_opportunities,
        priorities):
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

    def sample_opportunities(
        self,
        sorted_collected_opportunities):
        """ Generates a graph from discretized Data Take Opportunities
        """

        # build graph, and add nodes
        graph = nx.Graph()

        # first sample opportunities at random
        opportunities = []
        for satellite_id, requests_opportunities in enumerate(sorted_collected_opportunities):
            for request_id, local_opportunities in enumerate(requests_opportunities):
                if len(local_opportunities) <= 0:
                    continue
                collect_opportunity = random.choice(local_opportunities)
                opportunities.append(collect_opportunity)
        return opportunities

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
        with open(f"graphs_{self.delta_t}/{self.prefix}_subgraph_{graph_id}.nx", 'wb') as file:
            pickle.dump(graph, file)

    def run(self,
            dtos,
            requests,
            priorities,
            satellites,
            max_subgraph_size=80,
            start_dates=None,
            allow_requests=None,
            discretizing_array=None,
            greedy=True,
            split_into_subgraphs=False,
            save_graphs=False
            plot_graphs=False):
        """ Run
        """
        self.dashboard = MetricsDashboard()
        self.dashboard.start_recording()
        self.dashboard.overlap_complexity.compute(dtos)

        self.satellites = satellites
        self.priorities = priorities
        self.num_satellites = len(satellites)
        self.num_requests = len(priorities)
        self.requests_positions = requests

        # discretize data take opportunities
        collect_opportunities, sorted_collected_opportunities = self.discretize_dtos( \
                dtos,
                priorities)

        if greedy:
            opportunities = collect_opportunities
        else:
            opportunities = self.sample_opportunities(sorted_collected_opportunities)

        graph = self.graph_from_collect_opportunities(
            opportunities,
            priorities)

        if save_graphs:
            self.save_graph("total", graph)
    
        if plot_graphs:
            postprocessor = Postprocessor(self.num_satellites, self.num_requests)
            postprocessor.plot_graph(graph, prefix=f"graphs_{self.delta_t}/{self.prefix}_total")


        # compute Maximum Independent Set
        mis = self.get_maximum_independent_set(graph)

        # split into subgraphs
        if split_into_subgraphs:

            subgraphs = [graph.subgraph(c) for c in nx.connected_components(graph)]

            for graph_id, subgraph in enumerate(subgraphs):
                subgraph_len = len(subgraph)
                pos = nx.get_node_attributes(subgraph, "pos")
                subgraph = nx.convert_node_labels_to_integers(subgraph)

                if save_graphs:
                    self.save_graph(graph_id, subgraph)

                if plot_graphs:
                    postprocessor = Postprocessor(self.num_satellites, self.num_requests)
                    postprocessor.plot_graph(
                        subgraph,
                        prefix=f"graphs_{self.delta_t}/{self.prefix}_{graph_id}")

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

        self.dashboard.update()
        self.dashboard.save(self.prefix)

        results = {}
        for metric in self.dashboard.metrics:
            results[f"{metric.name}"] = metric.data

        with open(f'{self.prefix}_result.json', 'w') as f:
            json.dump(results, f)
        
        # save mis into results
        results["mis"] = mis

        return graph, results
