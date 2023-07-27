from app.dto.common import BaseResponseData
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponseData(BaseModel):
    access_token: str

class LoginResponse(BaseResponseData):
    data: LoginResponseData