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
        db.execute("""SELECT anmethodref_select AS sop FROM mc.vw_tabel_including_archive GROUP BY anmethodref_select ORDER BY anmethodref_select;""")
        sops = db.fetchall()
    return sops

@router.get('/user', response_model=List[Sop])
def get_sops_based_on_user(current_user: str = Depends(get_current_user)):

    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        team_id = current_user.team_id
        db.execute("""SELECT anmethodref AS sop FROM mc.team_sop WHERE team_id = %s""", (str(team_id),))
        sops = db.fetchall()

    return sops