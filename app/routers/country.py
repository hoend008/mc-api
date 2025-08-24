from fastapi import APIRouter, Depends
from typing import List
from DB.DBconnection import PostgresDatabase
from schemas.schemas import Country
from utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/countries",
    tags=["countries"])


@router.get("/", response_model=List[Country])
def get_countries(current_user: int = Depends(get_current_user)) -> List[Country]:
    with PostgresDatabase() as db:
        db.execute("""SELECT c.id, c.code2, c.code3, c.country FROM ontologies.country c JOIN ews.sample s ON c.id = s.country_id GROUP BY c.id, c.code2, c.code3, c.country;""")
        countries = db.fetchall()
    return countries