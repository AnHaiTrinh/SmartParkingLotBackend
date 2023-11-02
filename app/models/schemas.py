from enum import Enum
from typing import Union

from pydantic import BaseModel
from datetime import datetime


class BaseUser(BaseModel):
    username: str


class UserCreate(BaseUser):
    password: str


class UserOut(BaseUser):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserUpdate(BaseModel):
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenType(str, Enum):
    access_token = 'access'
    refresh_token = 'refresh'


class TokenData(BaseModel):
    token_type: TokenType
    token: str
