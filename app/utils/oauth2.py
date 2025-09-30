import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jwt.exceptions import InvalidTokenError
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from DB.PostgresDatabasev2 import PostgresDatabase
from schemas.schemas import User, UserInDB, TokenData
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME

#SECRET_KEY = os.getenv("SECRET_KEY")
#ALGORITHM = os.getenv("ALGORITHM")

SECRET_KEY = "9wyyLgGcxqMcD5xxdMCQGhKMHHMap5vX3CTu7e5FtyYVQdHMrkhY8wUJq5adxJpCq2RTQYSVXBM"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
                                     

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str) -> UserInDB:
    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        db.execute("""SELECT * FROM administration.users WHERE username = %s""", (username,))
        user = db.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserInDB(**user)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    #if not user:
    #    return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user