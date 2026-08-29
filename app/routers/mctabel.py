from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import execute_values
from typing import List

from schemas.schemas import MCTabel, MCTabelSaveResponse
from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from utils.oauth2 import get_current_user


router = APIRouter(
    prefix="/mctabel",
    tags=["mctable test"],
)

MCTABEL_COLUMNS = ('id', 'team_id', 'groupori', 'use', 'productgroup_id', 'sample_matrix', 'e02_sampmatcode1_en', 'e02_sampmatcode1_nl', 'e02_sampmatcode2_en', 'e02_sampmatcode2_nl', 'e02_sampmatcode3_en', 'e02_sampmatcode3_nl', 'e02_sampmatcode4_en', 'e02_sampmatcode4_nl', 'mtx_id', 'substance_group', 'param_id', 'param_termextendedname', 'paramtext_lims', 'paramtext_abbreviation', 'paramtyp_id', 'anmethodref', 'flex_scope_no', 'qual_quan_method', 'anlytyp_id', 'anlymd_id', 'mdacc_id', 'resinfo', 'resunit_wfsr', 'unit_id', 'exprres_id', 'lod', 'loq', 'ccalpha', 'ccbeta', 'resvaluncert', 'evallowlimit', 'actionlevel', 'lmttyp_id', 'confirmation_sop', 'lu_s_productid', 'detailedcom', 'val_report_name', 'val_report_date', 'matrix_cal_curve', 'measuring_range', 'trueness_j_recovery', 'rsdr', 'rsdwr_rsdrl', 'mutation_date', 'plan_nvwa_year', 'remarks', 'insert_date', 'sheetname',)


@router.get("", response_model=List[MCTabel])
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
    """.replace("\n", "")

    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=True) as db:
        db.execute(query)
        rows = db.fetchall()

    return rows


@router.post("/save", response_model=MCTabelSaveResponse)
def save_mctabel(
    rows: List[MCTabel],
    current_user: int = Depends(get_current_user),
):
    if not rows:
        return MCTabelSaveResponse(received=0, inserted=0, updated=0, unchanged=0)

    keys = [(row.sheetname, row.id) for row in rows]
    if len(keys) != len(set(keys)):
        raise HTTPException(
            status_code=400,
            detail="The submitted data contains duplicate (sheetname, id) combinations.",
        )

    create_temp_sql = """
        CREATE TEMP TABLE tmp_mctabel_save
        (LIKE mc.tabel_output INCLUDING DEFAULTS)
        ON COMMIT DROP;
    """

    insert_temp_sql = f"""
        INSERT INTO tmp_mctabel_save ({", ".join(MCTABEL_COLUMNS)})
        VALUES %s
    """

    lock_existing_sql = """
        SELECT output.id
        FROM mc.tabel_output AS output
        INNER JOIN tmp_mctabel_save AS incoming
            ON incoming.sheetname = output.sheetname
           AND incoming.id = output.id
        FOR UPDATE OF output;
    """

    archive_sql = """
        INSERT INTO mc.tabel_output_archive (
            id, team_id, groupori, use, productgroup_id, sample_matrix, e02_sampmatcode1_en, e02_sampmatcode1_nl, e02_sampmatcode2_en, e02_sampmatcode2_nl, e02_sampmatcode3_en, e02_sampmatcode3_nl, e02_sampmatcode4_en, e02_sampmatcode4_nl, mtx_id, substance_group, param_id, param_termextendedname, paramtext_lims, paramtext_abbreviation, paramtyp_id, anmethodref, flex_scope_no, qual_quan_method, anlytyp_id, anlymd_id, mdacc_id, resinfo, resunit_wfsr, unit_id, exprres_id, lod, loq, ccalpha, ccbeta, resvaluncert, evallowlimit, actionlevel, lmttyp_id, confirmation_sop, lu_s_productid, detailedcom, val_report_name, val_report_date, matrix_cal_curve, measuring_range, trueness_j_recovery, rsdr, rsdwr_rsdrl, mutation_date, plan_nvwa_year, remarks, insert_date, sheetname
        )
        SELECT
            output.id, output.team_id, output.groupori, output.use, output.productgroup_id, output.sample_matrix, output.e02_sampmatcode1_en, output.e02_sampmatcode1_nl, output.e02_sampmatcode2_en, output.e02_sampmatcode2_nl, output.e02_sampmatcode3_en, output.e02_sampmatcode3_nl, output.e02_sampmatcode4_en, output.e02_sampmatcode4_nl, output.mtx_id, output.substance_group, output.param_id, output.param_termextendedname, output.paramtext_lims, output.paramtext_abbreviation, output.paramtyp_id, output.anmethodref, output.flex_scope_no, output.qual_quan_method, output.anlytyp_id, output.anlymd_id, output.mdacc_id, output.resinfo, output.resunit_wfsr, output.unit_id, output.exprres_id, output.lod, output.loq, output.ccalpha, output.ccbeta, output.resvaluncert, output.evallowlimit, output.actionlevel, output.lmttyp_id, output.confirmation_sop, output.lu_s_productid, output.detailedcom, output.val_report_name, output.val_report_date, output.matrix_cal_curve, output.measuring_range, output.trueness_j_recovery, output.rsdr, output.rsdwr_rsdrl, output.mutation_date, output.plan_nvwa_year, output.remarks, output.insert_date, output.sheetname
        FROM mc.tabel_output AS output
        INNER JOIN tmp_mctabel_save AS incoming
            ON incoming.sheetname = output.sheetname
           AND incoming.id = output.id
        WHERE ROW(output.team_id, output.groupori, output.use, output.productgroup_id, output.sample_matrix, output.e02_sampmatcode1_en, output.e02_sampmatcode1_nl, output.e02_sampmatcode2_en, output.e02_sampmatcode2_nl, output.e02_sampmatcode3_en, output.e02_sampmatcode3_nl, output.e02_sampmatcode4_en, output.e02_sampmatcode4_nl, output.mtx_id, output.substance_group, output.param_id, output.param_termextendedname, output.paramtext_lims, output.paramtext_abbreviation, output.paramtyp_id, output.anmethodref, output.flex_scope_no, output.qual_quan_method, output.anlytyp_id, output.anlymd_id, output.mdacc_id, output.resinfo, output.resunit_wfsr, output.unit_id, output.exprres_id, output.lod, output.loq, output.ccalpha, output.ccbeta, output.resvaluncert, output.evallowlimit, output.actionlevel, output.lmttyp_id, output.confirmation_sop, output.lu_s_productid, output.detailedcom, output.val_report_name, output.val_report_date, output.matrix_cal_curve, output.measuring_range, output.trueness_j_recovery, output.rsdr, output.rsdwr_rsdrl, output.mutation_date, output.plan_nvwa_year, output.remarks, output.insert_date)
              IS DISTINCT FROM
              ROW(incoming.team_id, incoming.groupori, incoming.use, incoming.productgroup_id, incoming.sample_matrix, incoming.e02_sampmatcode1_en, incoming.e02_sampmatcode1_nl, incoming.e02_sampmatcode2_en, incoming.e02_sampmatcode2_nl, incoming.e02_sampmatcode3_en, incoming.e02_sampmatcode3_nl, incoming.e02_sampmatcode4_en, incoming.e02_sampmatcode4_nl, incoming.mtx_id, incoming.substance_group, incoming.param_id, incoming.param_termextendedname, incoming.paramtext_lims, incoming.paramtext_abbreviation, incoming.paramtyp_id, incoming.anmethodref, incoming.flex_scope_no, incoming.qual_quan_method, incoming.anlytyp_id, incoming.anlymd_id, incoming.mdacc_id, incoming.resinfo, incoming.resunit_wfsr, incoming.unit_id, incoming.exprres_id, incoming.lod, incoming.loq, incoming.ccalpha, incoming.ccbeta, incoming.resvaluncert, incoming.evallowlimit, incoming.actionlevel, incoming.lmttyp_id, incoming.confirmation_sop, incoming.lu_s_productid, incoming.detailedcom, incoming.val_report_name, incoming.val_report_date, incoming.matrix_cal_curve, incoming.measuring_range, incoming.trueness_j_recovery, incoming.rsdr, incoming.rsdwr_rsdrl, incoming.mutation_date, incoming.plan_nvwa_year, incoming.remarks, incoming.insert_date);
    """

    upsert_sql = """
        INSERT INTO mc.tabel_output (
            id, team_id, groupori, use, productgroup_id, sample_matrix, e02_sampmatcode1_en, e02_sampmatcode1_nl, e02_sampmatcode2_en, e02_sampmatcode2_nl, e02_sampmatcode3_en, e02_sampmatcode3_nl, e02_sampmatcode4_en, e02_sampmatcode4_nl, mtx_id, substance_group, param_id, param_termextendedname, paramtext_lims, paramtext_abbreviation, paramtyp_id, anmethodref, flex_scope_no, qual_quan_method, anlytyp_id, anlymd_id, mdacc_id, resinfo, resunit_wfsr, unit_id, exprres_id, lod, loq, ccalpha, ccbeta, resvaluncert, evallowlimit, actionlevel, lmttyp_id, confirmation_sop, lu_s_productid, detailedcom, val_report_name, val_report_date, matrix_cal_curve, measuring_range, trueness_j_recovery, rsdr, rsdwr_rsdrl, mutation_date, plan_nvwa_year, remarks, insert_date, sheetname
        )
        SELECT
            id, team_id, groupori, use, productgroup_id, sample_matrix, e02_sampmatcode1_en, e02_sampmatcode1_nl, e02_sampmatcode2_en, e02_sampmatcode2_nl, e02_sampmatcode3_en, e02_sampmatcode3_nl, e02_sampmatcode4_en, e02_sampmatcode4_nl, mtx_id, substance_group, param_id, param_termextendedname, paramtext_lims, paramtext_abbreviation, paramtyp_id, anmethodref, flex_scope_no, qual_quan_method, anlytyp_id, anlymd_id, mdacc_id, resinfo, resunit_wfsr, unit_id, exprres_id, lod, loq, ccalpha, ccbeta, resvaluncert, evallowlimit, actionlevel, lmttyp_id, confirmation_sop, lu_s_productid, detailedcom, val_report_name, val_report_date, matrix_cal_curve, measuring_range, trueness_j_recovery, rsdr, rsdwr_rsdrl, mutation_date, plan_nvwa_year, remarks, insert_date, sheetname
        FROM tmp_mctabel_save
        ON CONFLICT (sheetname, id)
        DO UPDATE SET
            team_id = EXCLUDED.team_id,
            groupori = EXCLUDED.groupori,
            use = EXCLUDED.use,
            productgroup_id = EXCLUDED.productgroup_id,
            sample_matrix = EXCLUDED.sample_matrix,
            e02_sampmatcode1_en = EXCLUDED.e02_sampmatcode1_en,
            e02_sampmatcode1_nl = EXCLUDED.e02_sampmatcode1_nl,
            e02_sampmatcode2_en = EXCLUDED.e02_sampmatcode2_en,
            e02_sampmatcode2_nl = EXCLUDED.e02_sampmatcode2_nl,
            e02_sampmatcode3_en = EXCLUDED.e02_sampmatcode3_en,
            e02_sampmatcode3_nl = EXCLUDED.e02_sampmatcode3_nl,
            e02_sampmatcode4_en = EXCLUDED.e02_sampmatcode4_en,
            e02_sampmatcode4_nl = EXCLUDED.e02_sampmatcode4_nl,
            mtx_id = EXCLUDED.mtx_id,
            substance_group = EXCLUDED.substance_group,
            param_id = EXCLUDED.param_id,
            param_termextendedname = EXCLUDED.param_termextendedname,
            paramtext_lims = EXCLUDED.paramtext_lims,
            paramtext_abbreviation = EXCLUDED.paramtext_abbreviation,
            paramtyp_id = EXCLUDED.paramtyp_id,
            anmethodref = EXCLUDED.anmethodref,
            flex_scope_no = EXCLUDED.flex_scope_no,
            qual_quan_method = EXCLUDED.qual_quan_method,
            anlytyp_id = EXCLUDED.anlytyp_id,
            anlymd_id = EXCLUDED.anlymd_id,
            mdacc_id = EXCLUDED.mdacc_id,
            resinfo = EXCLUDED.resinfo,
            resunit_wfsr = EXCLUDED.resunit_wfsr,
            unit_id = EXCLUDED.unit_id,
            exprres_id = EXCLUDED.exprres_id,
            lod = EXCLUDED.lod,
            loq = EXCLUDED.loq,
            ccalpha = EXCLUDED.ccalpha,
            ccbeta = EXCLUDED.ccbeta,
            resvaluncert = EXCLUDED.resvaluncert,
            evallowlimit = EXCLUDED.evallowlimit,
            actionlevel = EXCLUDED.actionlevel,
            lmttyp_id = EXCLUDED.lmttyp_id,
            confirmation_sop = EXCLUDED.confirmation_sop,
            lu_s_productid = EXCLUDED.lu_s_productid,
            detailedcom = EXCLUDED.detailedcom,
            val_report_name = EXCLUDED.val_report_name,
            val_report_date = EXCLUDED.val_report_date,
            matrix_cal_curve = EXCLUDED.matrix_cal_curve,
            measuring_range = EXCLUDED.measuring_range,
            trueness_j_recovery = EXCLUDED.trueness_j_recovery,
            rsdr = EXCLUDED.rsdr,
            rsdwr_rsdrl = EXCLUDED.rsdwr_rsdrl,
            mutation_date = EXCLUDED.mutation_date,
            plan_nvwa_year = EXCLUDED.plan_nvwa_year,
            remarks = EXCLUDED.remarks,
            insert_date = EXCLUDED.insert_date
        WHERE ROW(mc.tabel_output.team_id, mc.tabel_output.groupori, mc.tabel_output.use, mc.tabel_output.productgroup_id, mc.tabel_output.sample_matrix, mc.tabel_output.e02_sampmatcode1_en, mc.tabel_output.e02_sampmatcode1_nl, mc.tabel_output.e02_sampmatcode2_en, mc.tabel_output.e02_sampmatcode2_nl, mc.tabel_output.e02_sampmatcode3_en, mc.tabel_output.e02_sampmatcode3_nl, mc.tabel_output.e02_sampmatcode4_en, mc.tabel_output.e02_sampmatcode4_nl, mc.tabel_output.mtx_id, mc.tabel_output.substance_group, mc.tabel_output.param_id, mc.tabel_output.param_termextendedname, mc.tabel_output.paramtext_lims, mc.tabel_output.paramtext_abbreviation, mc.tabel_output.paramtyp_id, mc.tabel_output.anmethodref, mc.tabel_output.flex_scope_no, mc.tabel_output.qual_quan_method, mc.tabel_output.anlytyp_id, mc.tabel_output.anlymd_id, mc.tabel_output.mdacc_id, mc.tabel_output.resinfo, mc.tabel_output.resunit_wfsr, mc.tabel_output.unit_id, mc.tabel_output.exprres_id, mc.tabel_output.lod, mc.tabel_output.loq, mc.tabel_output.ccalpha, mc.tabel_output.ccbeta, mc.tabel_output.resvaluncert, mc.tabel_output.evallowlimit, mc.tabel_output.actionlevel, mc.tabel_output.lmttyp_id, mc.tabel_output.confirmation_sop, mc.tabel_output.lu_s_productid, mc.tabel_output.detailedcom, mc.tabel_output.val_report_name, mc.tabel_output.val_report_date, mc.tabel_output.matrix_cal_curve, mc.tabel_output.measuring_range, mc.tabel_output.trueness_j_recovery, mc.tabel_output.rsdr, mc.tabel_output.rsdwr_rsdrl, mc.tabel_output.mutation_date, mc.tabel_output.plan_nvwa_year, mc.tabel_output.remarks, mc.tabel_output.insert_date)
              IS DISTINCT FROM
              ROW(EXCLUDED.team_id, EXCLUDED.groupori, EXCLUDED.use, EXCLUDED.productgroup_id, EXCLUDED.sample_matrix, EXCLUDED.e02_sampmatcode1_en, EXCLUDED.e02_sampmatcode1_nl, EXCLUDED.e02_sampmatcode2_en, EXCLUDED.e02_sampmatcode2_nl, EXCLUDED.e02_sampmatcode3_en, EXCLUDED.e02_sampmatcode3_nl, EXCLUDED.e02_sampmatcode4_en, EXCLUDED.e02_sampmatcode4_nl, EXCLUDED.mtx_id, EXCLUDED.substance_group, EXCLUDED.param_id, EXCLUDED.param_termextendedname, EXCLUDED.paramtext_lims, EXCLUDED.paramtext_abbreviation, EXCLUDED.paramtyp_id, EXCLUDED.anmethodref, EXCLUDED.flex_scope_no, EXCLUDED.qual_quan_method, EXCLUDED.anlytyp_id, EXCLUDED.anlymd_id, EXCLUDED.mdacc_id, EXCLUDED.resinfo, EXCLUDED.resunit_wfsr, EXCLUDED.unit_id, EXCLUDED.exprres_id, EXCLUDED.lod, EXCLUDED.loq, EXCLUDED.ccalpha, EXCLUDED.ccbeta, EXCLUDED.resvaluncert, EXCLUDED.evallowlimit, EXCLUDED.actionlevel, EXCLUDED.lmttyp_id, EXCLUDED.confirmation_sop, EXCLUDED.lu_s_productid, EXCLUDED.detailedcom, EXCLUDED.val_report_name, EXCLUDED.val_report_date, EXCLUDED.matrix_cal_curve, EXCLUDED.measuring_range, EXCLUDED.trueness_j_recovery, EXCLUDED.rsdr, EXCLUDED.rsdwr_rsdrl, EXCLUDED.mutation_date, EXCLUDED.plan_nvwa_year, EXCLUDED.remarks, EXCLUDED.insert_date);
    """

    values = [(row.id, row.team_id, row.groupori, row.use, row.productgroup_id, row.sample_matrix, row.e02_sampmatcode1_en, row.e02_sampmatcode1_nl, row.e02_sampmatcode2_en, row.e02_sampmatcode2_nl, row.e02_sampmatcode3_en, row.e02_sampmatcode3_nl, row.e02_sampmatcode4_en, row.e02_sampmatcode4_nl, row.mtx_id, row.substance_group, row.param_id, row.param_termextendedname, row.paramtext_lims, row.paramtext_abbreviation, row.paramtyp_id, row.anmethodref, row.flex_scope_no, row.qual_quan_method, row.anlytyp_id, row.anlymd_id, row.mdacc_id, row.resinfo, row.resunit_wfsr, row.unit_id, row.exprres_id, row.lod, row.loq, row.ccalpha, row.ccbeta, row.resvaluncert, row.evallowlimit, row.actionlevel, row.lmttyp_id, row.confirmation_sop, row.lu_s_productid, row.detailedcom, row.val_report_name, row.val_report_date, row.matrix_cal_curve, row.measuring_range, row.trueness_j_recovery, row.rsdr, row.rsdwr_rsdrl, row.mutation_date, row.plan_nvwa_year, row.remarks, row.insert_date, row.sheetname) for row in rows]

    with PostgresDatabase(DB_NAME, DB_USER, DB_PASSWORD, realdictcursor=False) as db:
        try:
            db.execute(create_temp_sql)

            execute_values(
                db.cursor,
                insert_temp_sql,
                values,
                page_size=1000,
            )

            db.execute(lock_existing_sql)

            db.execute(archive_sql)
            updated_count = db.cursor.rowcount

            db.execute(upsert_sql)
            affected_count = db.cursor.rowcount

            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to save table data.",
            ) from exc

    inserted_count = affected_count - updated_count
    unchanged_count = len(rows) - affected_count

    return MCTabelSaveResponse(
        received=len(rows),
        inserted=inserted_count,
        updated=updated_count,
        unchanged=unchanged_count,
    )
