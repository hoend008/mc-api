from fastapi import status, HTTPException, APIRouter, Depends
from DB.PostgresDatabasev2 import PostgresDatabase
from schemas.schemas import UserCreate, UserOut
from utils.oauth2 import get_current_user, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: UserCreate):
    
    # hash password
    hashed_pwd = get_password_hash(user.hashed_password)
    user.hashed_password = hashed_pwd
    
    with PostgresDatabase() as db:
        db.execute("""INSERT INTO administration.users(username, hashed_password) VALUES (%s, %s) RETURNING *""",
                   (user.username, user.hashed_password))
        created_user = db.fetchone()
        db.commit()
    return created_user

@router.get('/{id}', response_model=UserOut)
def get_user(id: int, current_user: int = Depends(get_current_user)):
    with PostgresDatabase() as db:
        db.execute("""SELECT * FROM administration.users WHERE id = %s""", (str(id),))
        user = db.fetchone()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exists")
    return user  