from fastapi import APIRouter, Depends
from typing import List
from DB.DBconnection import PostgresDatabase
from schemas.schemas import Count, SampleYears, SampleCountry
from utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/samples",
    tags=["samples"])


@router.get("/count", response_model=Count)
def get_samples_count(country_id: int = None, feedconversion_id: int = None, current_user: int = Depends(get_current_user)) -> Count:
    
    # construct query based on path parameters
    if country_id:
        country_query = f"country_id = {country_id}"
    else:
        country_query = "1 = 1"

    if feedconversion_id:
        feedconversion_query = f"feedconversion_id = {feedconversion_id}"
    else:
        feedconversion_query = "1 = 1"

    # fetch data
    with PostgresDatabase() as db:
        db.execute("SELECT COUNT(*) FROM ews.sample WHERE " + country_query + " AND " + feedconversion_query + ";")
        samples = db.fetchone()

    # return result
    return samples

@router.get("/years", response_model=List[SampleYears])
def get_samples_years(iso_a3: str = None, feedconversion_id: int = None, current_user: int = Depends(get_current_user)) -> List[SampleYears]:
    
    # construct query based on path parameters
    start_query = "SELECT year_harvest AS year, COUNT(*) AS count FROM ews.vw_sample WHERE "
    if iso_a3:
        country_query = f"iso_a3 = '{iso_a3.lower()}'"
    else:
        country_query = "1 = 1"

    if feedconversion_id:
        feedconversion_query = f"feedconversion_id = {feedconversion_id}"
    else:
        feedconversion_query = "1 = 1"

    end_query = " AND year_harvest IS NOT NULL GROUP BY year_harvest ORDER BY year_harvest;"

    query_final = start_query + country_query + " AND " + feedconversion_query + end_query
    
    # fetch data
    with PostgresDatabase() as db:
        db.execute(query_final)
        sample_years = db.fetchall()

    # return result
    return sample_years

@router.get("/countries", response_model=List[SampleCountry])
def get_samples_countries(current_user: int = Depends(get_current_user)) -> List[SampleCountry]:
    
    # construct query based on path parameters
    start_query = "SELECT LOWER(c.code3) AS iso_a3, COUNT(*) AS density FROM ews.sample s JOIN ontologies.country c ON s.country_id = c.id WHERE c.code3 <> '999'"
    end_query = " GROUP BY c.code3;"

    query_final = start_query + end_query
    
    # fetch data
    with PostgresDatabase() as db:
        db.execute(query_final)
        sample_countries = db.fetchall()

    # return result
    return sample_countries