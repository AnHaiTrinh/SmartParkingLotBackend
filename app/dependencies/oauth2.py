import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .db_connection import DatabaseDependency
from ..models.models import User
from ..utils.jwt import verify_jwt_token
from .redis_connection import RedisDependency

auth_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_current_user(db: DatabaseDependency, redis_client: RedisDependency, token: str = Depends(auth_scheme)):
    try:
        user_id = verify_jwt_token(token, secret_key=os.getenv('JWT_ACCESS_SECRET_KEY'), redis_client=redis_client)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Inactive user')
    return current_user


CurrentActiveUserDependency = Annotated[User, Depends(get_current_active_user)]
