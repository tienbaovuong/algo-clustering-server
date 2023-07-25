from typing import List
import numpy as np
from app.helpers.cluster.base_cluster import ClusterObject, ClusterService


class ThesisClusterObject(ClusterObject):
    title_vector: list
    category_vector: list
    expected_result_vector: list
    problem_solve_vector: list

def multiply_array(input: list, multiplier: float):
    result = []
    for item in input:
        result.append(item * multiplier)
    return result

def get_medium_array(input: list, total_uik: float):
    result = np.zeros_like(input[0])

    for item in input:
        result += np.array(item)
    
    result /= total_uik
    return result.tolist()


class ThesisClusterService(ClusterService):
    def __init__(self, field_weights, field_balance_multipliers):
        self.field_weights = field_weights
        self.field_balance_multipliers = field_balance_multipliers

    def get_distance_between_two_object(self, first_object: ThesisClusterObject, second_object: ThesisClusterObject) -> float:
        dis1 = np.linalg.norm(np.array(first_object.title_vector) - np.array(second_object.title_vector)) * self.field_weights[0] * self.field_balance_multipliers[0]
        dis2 = np.linalg.norm(np.array(first_object.category_vector) - np.array(second_object.category_vector)) * self.field_weights[1] * self.field_balance_multipliers[1]
        dis3 = np.linalg.norm(np.array(first_object.expected_result_vector) - np.array(second_object.expected_result_vector)) * self.field_weights[2] * self.field_balance_multipliers[2]
        dis4 = np.linalg.norm(np.array(first_object.problem_solve_vector) - np.array(second_object.problem_solve_vector)) * self.field_weights[3] * self.field_balance_multipliers[3]
        return dis1 + dis2 + dis3 + dis4
    
    def calculate_centroid_from_list_and_uik(self, uik_pow: list, data: List[ThesisClusterObject]) -> ThesisClusterObject:
        list_title = [multiply_array(item.title_vector, uik) for uik, item in zip(uik_pow, data)]
        list_category = [multiply_array(item.category_vector, uik) for uik, item in zip(uik_pow, data)]
        list_expected = [multiply_array(item.expected_result_vector, uik) for uik, item in zip(uik_pow, data)]
        list_problem = [multiply_array(item.problem_solve_vector, uik) for uik, item in zip(uik_pow, data)]
        
        total_uik = sum(uik_pow)
        new_centroid = ThesisClusterObject(
            title_vector=get_medium_array(list_title, total_uik),
            category_vector=get_medium_array(list_category, total_uik),
            expected_result_vector=get_medium_array(list_expected, total_uik),
            problem_solve_vector=get_medium_array(list_problem, total_uik)
        )
        return new_centroid