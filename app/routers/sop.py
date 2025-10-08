from fastapi import APIRouter, Depends
from typing import List
from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from schemas.schemas import Sop
from utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/sop",
    tags=["sop"])


@router.get("/", response_model=List[Sop])
def get_sop(current_user: int = Depends(get_current_user)) -> List[Sop]:
    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        db.execute("""SELECT anmethodref AS sop FROM mc.tabel_test GROUP BY anmethodref ORDER BY anmethodref;""")
        sops = db.fetchall()
    return sops