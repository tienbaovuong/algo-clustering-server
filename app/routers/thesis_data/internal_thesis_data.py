from fastapi import APIRouter
from app.dto.common import BaseResponse
from app.dto.thesis_data_dto import ThesisDataUpdateNlpRequest
from app.services.thesis_data_service import ThesisDataService

internal_route = APIRouter(tags=['Thesis Data'], prefix="/thesis_data")


@internal_route.put(
    '/{thesis_id}/update_nlp',
    response_model=BaseResponse
)
async def update_thesis_nlp_data(
    thesis_id: str,
    data: ThesisDataUpdateNlpRequest,
):
    await ThesisDataService().update_nlp(
        thesis_id=thesis_id,
        title_vector=data.title_vector,
        category_vector=data.category_vector,
        expected_result=data.expected_result,
        problem_solve=data.problem_solve
    )

    return BaseResponse(
        message=f"Update nlp successfully for thesis id {thesis_id}"
    )
