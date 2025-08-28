from fastapi import APIRouter, Depends
from typing import List
from DB.DBconnection import PostgresDatabase
from schemas.schemas import Prediction
from utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"])


@router.get("/", response_model=List[Prediction])
def get_predictions(current_user: int = Depends(get_current_user)) -> List[Prediction]:
    with PostgresDatabase() as db:
        db.execute("""SELECT code3, ROUND(AVG(average_probability), 3) AS value FROM ews.vw_model_predictions_average GROUP BY code3;""")
        predictions = db.fetchall()
    return predictions