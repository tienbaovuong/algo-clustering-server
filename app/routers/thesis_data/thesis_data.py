from datetime import datetime

from fastapi import APIRouter, Query, Depends, UploadFile, File
from pymongo.errors import DuplicateKeyError

from app.dto.common import (BaseResponse, BaseResponseData)
from app.helpers.auth_helpers import get_current_user
from app.dto.thesis_data_dto import (ThesisDataResponse, ThesisDataPaginationResponse, ThesisDataPaginationData, ThesisDataCreateRequest)
from app.services.thesis_data_service import ThesisDataService
from app.helpers.exceptions import ThesisWrongFormatException

route = APIRouter(tags=['Thesis Data'], prefix="/thesis_data")


@route.get(
    '/list',
    response_model=ThesisDataPaginationResponse,
)
async def get_list_thesis_data(
    user: str = Depends(get_current_user),
    title: str = Query(None),
    semester: str = Query(None),
    created_at: str = Query(None),
    page: int = Query(1),
    limit: int = Query(10),
):
    if created_at:
        created_at = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    items, total = await ThesisDataService().list_thesis(
        title=title,
        semester=semester,
        created_at=created_at,
        page=page,
        limit=limit,
    )

    return ThesisDataPaginationResponse(
        message="Get list thesis successfully",
        data=ThesisDataPaginationData(
            items=items,
            total=total,
        )
    )


@route.get(
    '/{thesis_id}',
    response_model=ThesisDataResponse
)
async def get_thesis_data_by_id(
    thesis_id: str,
    user: str = Depends(get_current_user),
):
    thesis_data = await ThesisDataService().get(
        thesis_id=thesis_id,
    )

    return ThesisDataResponse(
        message="Get thesis successfully",
        data=thesis_data
    )


@route.post(
    '/create',
    response_model=BaseResponseData,
)
async def create_thesis_data(
    file: UploadFile = File(...),
    user: str = Depends(get_current_user),
):
    try:
        created_thesis_id = await ThesisDataService().create(
            file=file,
        )
    except DuplicateKeyError:
        return BaseResponse(
            error_code=1,
            message="Duplicated thesis"
        )
    except ThesisWrongFormatException:
        return BaseResponse(
            error_code=2,
            message="Wrong format or missing data"
        )
    return BaseResponseData(
        message="Created thesis successfully",
        data=created_thesis_id
    )


@route.delete(
    '/{thesis_id}',
    response_model=BaseResponse
)
async def delete_thesis_by_id(
    thesis_id: str,
    user: str = Depends(get_current_user),
):
    await ThesisDataService().delete(
        thesis_id=thesis_id
    )

    return BaseResponse(
        message="Deleted thesis successfully"
    )