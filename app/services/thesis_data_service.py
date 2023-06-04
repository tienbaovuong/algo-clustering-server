from typing import Optional
from datetime import datetime
from app.dto.thesis_data_dto import ThesisDataCreateRequest

class ThesisDataService:
    async def list(
        self,
        title: Optional[str],
        semester: Optional[str],
        created_at: Optional[datetime],
        page: int = 1,
        limit: int = 10,
    ):
        pass

    async def get(
        self,
        thesis_id: str
    ):
        pass

    async def create(
        self,
        thesis_input: ThesisDataCreateRequest,
    ):
        pass

    async def delete(
        self,
        thesis_id: str
    ):
        pass