from fastapi import status, APIRouter, Depends, HTTPException
import pandas as pd
import numpy as np
from typing import List
from schemas.schemas import MCdata, MCdataIn, ReturnMessage, MCdataOut
from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from utils.oauth2 import get_current_user
from utils.column_conversion import cols_conversion_dict
from utils.datatype_conversion import datatype_conversion_dict

import warnings
warnings.filterwarnings('ignore')

router = APIRouter(
    prefix="/mcdata",
    tags=["mcdata"])

@router.get('/', response_model=List[MCdataOut])
def get_user(current_user: int = Depends(get_current_user)):
    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        db.execute("""SELECT * FROM mc.tabel_test""")
        mcdata = db.fetchall()
    if not mcdata:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="MC data not found")
    return mcdata  


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReturnMessage)
def insert_mcdata(mcdata: List[MCdataIn], current_user: int = Depends(get_current_user)) -> ReturnMessage:

  """
  CREATE DATAFRAME FROM mcdata
  """
  df = pd.DataFrame([model.dict() for model in mcdata])

  """
  REMOVE ROWS WITHOUT team_id
  """
  df = df.query("team_id == team_id")

  """
  RENAME COLUMNS IN df
  """
  df = df.rename(columns=cols_conversion_dict)

  """
  CONVERT DATATYPE
  """
  for col in df.columns:
      # get datatype
      dt = datatype_conversion_dict[col]
      
      # set datatype
      if dt == 'date':
          df[col] = df[col].dt.date
      else:
          # set datatype
          df[col] = df[col].astype(dt)

  """
  REPLACE NAN WITH EMPTY STRING
  """
  df = df.replace('nan', '')

  """
  ADD MISSING COLUMNS
  """
  for col in datatype_conversion_dict.keys():
      if col not in df.columns:
          df[col] = np.nan

  """
  TEMPORARY
  """
  # df['identifier'] = 1

  """
  SAVE TO DB
  """
  with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD) as db:
      db.insert_update(df.copy(), 
                       'mc.tabel_test', 
                       update_existing=['identifier', 'team_id'],
                       text_output=False)   

      return {"msg": "Data successfully updated"}