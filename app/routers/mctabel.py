from fastapi import APIRouter, Depends
from typing import List

from schemas.schemas import MCTabel
from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from utils.oauth2 import get_current_user


router = APIRouter(
    prefix="/mctabel",
    tags=["mctable test"],
)


@router.get('', response_model=List[MCTabel])
def get_mctabel(
    current_user: int = Depends(get_current_user),
):
    query = """
        SELECT
            id,
            team_id,
            groupori,
            use,
            productgroup_id,
            sample_matrix,
            e02_sampmatcode1_en,
            e02_sampmatcode1_nl,
            e02_sampmatcode2_en,
            e02_sampmatcode2_nl,
            e02_sampmatcode3_en,
            e02_sampmatcode3_nl,
            e02_sampmatcode4_en,
            e02_sampmatcode4_nl,
            mtx_id,
            substance_group,
            param_id,
            param_termextendedname,
            paramtext_lims,
            paramtext_abbreviation,
            paramtyp_id,
            anmethodref,
            flex_scope_no,
            qual_quan_method,
            anlytyp_id,
            anlymd_id,
            mdacc_id,
            resinfo,
            resunit_wfsr,
            unit_id,
            exprres_id,
            lod,
            loq,
            ccalpha,
            ccbeta,
            resvaluncert,
            evallowlimit,
            actionlevel,
            lmttyp_id,
            confirmation_sop,
            lu_s_productid,
            detailedcom,
            val_report_name,
            val_report_date,
            matrix_cal_curve,
            measuring_range,
            trueness_j_recovery,
            rsdr,
            rsdwr_rsdrl,
            mutation_date,
            plan_nvwa_year,
            remarks,
            insert_date,
            sheetname 
        FROM mc.tabel 
        WHERE anmethodref = 'sop_a1396' 
        ORDER BY id;
    """.replace('\n', '')

    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        db.execute(query)
        rows = db.fetchall()

    return rows
