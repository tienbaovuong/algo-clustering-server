import sys
import math
import random
import numpy as np
from typing import List

from app.helpers.cluster.base_cluster import ClusterObject, ClusterService

# Base on SSMC-FMC
class ClusteringAlgorithm:
    def __init__(
        self,
        dataset: List[ClusterObject],
        model: ClusterService = ClusterService(),
        n_clusters: int = 3,
        max_size_cluster: int = 10,
        fuzzi_m: int = 2,
        alpha: float = 0.6,
        epsilon: float = 0.001,
        n_loop: int = 50,
    ) -> None:
        self.dataset = dataset
        self.model = model
        self.n_clusters = n_clusters
        self.max_size_cluster = max_size_cluster
        self.fuzzi_m = fuzzi_m
        self.alpha = alpha
        self.epsilon = epsilon
        self.membership = [[0] * self.n_clusters for _ in range(len(dataset))]
        self.centroid = []
        self.n_loop = n_loop
        self.is_stop = False
        self.pred_labels = [[] for _ in range(self.n_clusters)]
        self.loss_values = []

    def clustering(self):
        self._generate_centroid()
        th_loop = 1
        while th_loop <= self.n_loop and not self.is_stop:
            self.is_stop = True
            self._update_membership()
            self._update_centroid()
            self._calculate_loss_function()
            th_loop += 1
        for idx, membership in enumerate(self.membership):
            sorted_membership = sorted(membership, key=float, reverse=True)
            for data in sorted_membership:
                id_cluster = membership.index(data)
                if len(self.pred_labels[id_cluster]) < self.max_size_cluster:
                    self.pred_labels[id_cluster].append(idx)
                    break

        return self.pred_labels, self.loss_values

    def _generate_centroid(self):
        exclude_list = []
        # Set 1st centroid random
        first_centroid = random.randint(0, self.n_clusters - 1)
        self.centroid.append(self.dataset[first_centroid])
        exclude_list.append(first_centroid)

        # computing centroid furthest from the last centroid (greedy)
        for k in range(self.n_clusters - 1):
            random_list = list(set([i for i in range(0, self.n_clusters - 1)]) - set(exclude_list))
            next_centroid = random.choice(random_list)
            for i in range(len(self.dataset)):
                if i in exclude_list:
                    continue

                point = self.dataset[i]
                last_centroid = self.centroid[-1]

                d = sys.maxsize
                temp_dist = self._calculate_point_distance(last_centroid, point)
                if temp_dist < d:
                    next_centroid = i

            exclude_list.append(next_centroid)
            self.centroid.append(self.dataset[next_centroid])

    def _update_membership(self):

        fuzzi_m_pow = 1 / (self.fuzzi_m - 1)
        dij = [
            [
                self._calculate_point_distance(point, centroid)
                for centroid in self.centroid
            ]
            for point in self.dataset
        ]

        for id_point, point in enumerate(self.dataset):
            dij_pow = []
            sum_dij_pow = 0
            for id_centroid, centroid in enumerate(self.centroid):
                dik_pow = math.pow(dij[id_point][id_centroid], fuzzi_m_pow)
                dij_pow.append(dik_pow)
                sum_dij_pow += 1 / dik_pow

            membership = [1 / (dik_pow * sum_dij_pow) for dik_pow in dij_pow]
            self.membership[id_point] = membership

    def _update_centroid(self):
        th_centroid = []
        for id_centroid, centroid in enumerate(self.centroid):
            uik_pow = [
                math.pow(
                    self.membership[id_point][id_centroid],
                    self.fuzzi_m,
                )
                for id_point in range(len(self.dataset))
            ]
            new_centroid = self.model.calculate_centroid_from_list_and_uik(uik_pow=uik_pow, data=self.dataset)
            th_centroid.append(new_centroid)
            if self._calculate_point_distance(centroid, new_centroid) > self.epsilon:
                self.is_stop = False
        
        self.centroid = th_centroid

    def _calculate_point_distance(self, p1, p2):
        distance = self.model.get_distance_between_two_object(p1, p2)
        return distance if distance else self.epsilon

    def _calculate_loss_function(self):
        self.loss_values.append(
            sum(
                [
                    sum(
                        [
                            math.pow(
                                self.membership[id_point][id_centroid],
                                self.fuzzi_m,
                            )
                            * self._calculate_point_distance(point, centroid)
                            for id_centroid, centroid in enumerate(self.centroid)
                        ]
                    )
                    for id_point, point in enumerate(self.dataset)
                ]
            )
        )