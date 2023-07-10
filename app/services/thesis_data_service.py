from typing import Optional, List
from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import RegEx, GTE, Eq, In

from app.helpers.exceptions import NotFoundException
from app.dto.thesis_data_dto import ThesisDataCreateRequest, ShortThesisData, FullThesisData
from app.models.thesis_data import ThesisData
from app.worker.tasks.nlp_task import schedule_preprocess

class ThesisDataService:
    async def list_thesis(
        self,
        title: Optional[str],
        semester: Optional[str],
        created_at: Optional[datetime],
        page: int = 1,
        limit: int = 10,
    ):
        query = []
        skip = limit * (page - 1)
        if title:
            query.append(RegEx(ThesisData.title, title, options="i"))
        if semester:
            query.append(Eq(ThesisData.semester, semester))
        if created_at:
            query.append(GTE(ThesisData.created_at, created_at))
        if limit == -1:
            limit = None
        query_task = ThesisData.find_many(*query)
        total = await query_task.count()
        thesis_data_list = await query_task.skip(skip).limit(limit).sort(-ThesisData.id).project(ShortThesisData).to_list()
        return thesis_data_list, total

    async def get(
        self,
        thesis_id: str
    ):
        thesis_data = await ThesisData.find_one({'_id': PydanticObjectId(thesis_id)}).project(FullThesisData)
        if not thesis_data:
            raise NotFoundException("No thesis")
        return thesis_data

    async def create(
        self,
        thesis_input: ThesisDataCreateRequest,
    ):
        thesis_dict = thesis_input.dict()
        model = ThesisData(**thesis_dict)
        await model.save()
        schedule_preprocess(model.dict())
        return str(model.id)

    async def delete(
        self,
        thesis_id: str
    ):
        thesis = await ThesisData.find_one({'_id': PydanticObjectId(thesis_id)})
        if not thesis:
            raise NotFoundException("No thesis")
        await thesis.delete()

    async def get_list_by_ids(
        self,
        list_ids: List[str],
    ):
        new_list = []
        for id in list_ids:
            new_list.append(PydanticObjectId(id))
        thesis_list = await ThesisData.find_many(
            In(ThesisData.id, new_list)
        ).to_list()
        return thesis_list
    
    async def update_nlp(
        self,
        thesis_id: str,
        title_vector: List,
        category_vector: List,
        expected_result_vector: List,
        problem_solve_vector: List,
    ):
        update_data = {
            "title_vector": title_vector,
            "category_vector": category_vector,
            "expected_result_vector": expected_result_vector,
            "problem_solve_vector": problem_solve_vector,
            "updated_at": datetime.utcnow(),
            "need_nlp_extract": False
        }
        await ThesisData.find_one({'_id': PydanticObjectId(thesis_id)}).update({"$set": update_data})

    async def suggest_cluster_name(
        self,
        list_ids: List[str],
    ):
        thesis_list = await self.get_list_by_ids(list_ids)
        category_dict = {}
        for thesis in thesis_list:
            list_category = [word.strip().capitalize() for word in thesis.category.split(',')]
            for cate in list_category:
                if cate in category_dict.keys():
                    category_dict[cate] += 1
                else:
                    category_dict[cate] = 0

        order = sorted(category_dict, reverse=True)
        if len(order) > 1:
            return [order[0], order[1]]
        elif len(order) == 1:
            return [order[0]]
        return ["Default cluster name"]