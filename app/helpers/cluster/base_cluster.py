from pydantic import BaseModel
from typing import List

class ClusterObject(BaseModel):
    pass

class ClusterService():

    def get_distance_between_two_object(self, first_object: ClusterObject, second_object: ClusterObject) -> float:
        raise NotImplementedError()
    
    def calculate_centroid_from_list_and_uik(self, uik_pow: list, data: List[ClusterObject]) -> ClusterObject:
        raise NotImplementedError()
