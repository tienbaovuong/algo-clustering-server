from fastapi import APIRouter
from app.dto.common import (BaseResponse, BaseResponseData)

route = APIRouter(tags=['Thesis Data'], prefix="/thesis_data")