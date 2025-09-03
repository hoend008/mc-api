from fastapi import APIRouter, Depends
from typing import List
from DB.DBconnection import PostgresDatabase
from schemas.schemas import Count, SampleYears, SampleCountry, SampleProducts
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
def get_samples_years(iso_a3: str = None, year: int = None, feedconversion_id: int = None, current_user: int = Depends(get_current_user)) -> List[SampleYears]:
    
    # construct query based on path parameters
    start_query = "SELECT year_harvest AS year, COUNT(*) AS count FROM ews.vw_sample WHERE "
    if iso_a3:
        country_query = f"iso_a3 = '{iso_a3.lower()}'"
    else:
        country_query = "1 = 1"

    if year:
        year_query = f"year_harvest = {year}"
    else:
        year_query = "1 = 1"

    if feedconversion_id:
        feedconversion_query = f"feedconversion_id = {feedconversion_id}"
    else:
        feedconversion_query = "1 = 1"

    end_query = " AND year_harvest IS NOT NULL GROUP BY year_harvest ORDER BY year_harvest;"

    query_final = start_query + country_query + " AND " + year_query + " AND " + feedconversion_query + end_query
    
    # fetch data
    with PostgresDatabase() as db:
        db.execute(query_final)
        sample_years = db.fetchall()

    # return result
    return sample_years


@router.get("/products", response_model=List[SampleProducts])
def get_samples_products(iso_a3: str = None, year: int = None, current_user: int = Depends(get_current_user)) -> List[SampleYears]:
    
    # construct query based on path parameters
    start_query = "SELECT feedconversion_id, productname, COUNT(*) AS count FROM ews.vw_sample WHERE "
    if iso_a3:
        country_query = f"iso_a3 = '{iso_a3.lower()}'"
    else:
        country_query = "1 = 1"

    if year:
        year_query = f"year_harvest = {year}"
    else:
        year_query = "1 = 1"

    end_query = " AND productname IS NOT NULL GROUP BY feedconversion_id, productname ORDER BY COUNT(*) DESC LIMIT 3;"

    query_final = start_query + country_query + " AND " + year_query + end_query
    
    # fetch data
    with PostgresDatabase() as db:
        db.execute(query_final)
        sample_products = db.fetchall()

    # return result
    return sample_products


@router.get("/countries", response_model=List[SampleCountry])
def get_samples_countries(iso_a3: str = None, current_user: int = Depends(get_current_user)) -> List[SampleCountry]:
    
    # construct query based on path parameters
    start_query = "SELECT LOWER(iso_a3) AS iso_a3, COUNT(*) AS density FROM ews.vw_sample WHERE iso_a3 <> '999'"

    if iso_a3:
        country_query = f" AND iso_a3 = '{iso_a3.lower()}'"
    else:
        country_query = " AND 1 = 1"
        
    end_query = " GROUP BY iso_a3;"

    query_final = start_query + country_query + end_query
    print("----------------------------")
    print(query_final)
    # fetch data
    with PostgresDatabase() as db:
        db.execute(query_final)
        sample_countries = db.fetchall()

    # return result
    return sample_countries