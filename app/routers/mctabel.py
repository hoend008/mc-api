import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import execute_values

from schemas.schemas import MCTabel, MCTabelSaveResponse
from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from utils.oauth2 import get_current_user


logger = logging.getLogger(__name__)

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
        return MCTabelSaveResponse(
            received=0,
            inserted=0,
            updated=0,
            unchanged=0,
        )

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

    lock_output_sql = """
        LOCK TABLE mc.tabel_output
        IN SHARE ROW EXCLUSIVE MODE;
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

    update_existing_sql = """
        UPDATE mc.tabel_output AS output
        SET
            team_id = incoming.team_id,
            groupori = incoming.groupori,
            use = incoming.use,
            productgroup_id = incoming.productgroup_id,
            sample_matrix = incoming.sample_matrix,
            e02_sampmatcode1_en = incoming.e02_sampmatcode1_en,
            e02_sampmatcode1_nl = incoming.e02_sampmatcode1_nl,
            e02_sampmatcode2_en = incoming.e02_sampmatcode2_en,
            e02_sampmatcode2_nl = incoming.e02_sampmatcode2_nl,
            e02_sampmatcode3_en = incoming.e02_sampmatcode3_en,
            e02_sampmatcode3_nl = incoming.e02_sampmatcode3_nl,
            e02_sampmatcode4_en = incoming.e02_sampmatcode4_en,
            e02_sampmatcode4_nl = incoming.e02_sampmatcode4_nl,
            mtx_id = incoming.mtx_id,
            substance_group = incoming.substance_group,
            param_id = incoming.param_id,
            param_termextendedname = incoming.param_termextendedname,
            paramtext_lims = incoming.paramtext_lims,
            paramtext_abbreviation = incoming.paramtext_abbreviation,
            paramtyp_id = incoming.paramtyp_id,
            anmethodref = incoming.anmethodref,
            flex_scope_no = incoming.flex_scope_no,
            qual_quan_method = incoming.qual_quan_method,
            anlytyp_id = incoming.anlytyp_id,
            anlymd_id = incoming.anlymd_id,
            mdacc_id = incoming.mdacc_id,
            resinfo = incoming.resinfo,
            resunit_wfsr = incoming.resunit_wfsr,
            unit_id = incoming.unit_id,
            exprres_id = incoming.exprres_id,
            lod = incoming.lod,
            loq = incoming.loq,
            ccalpha = incoming.ccalpha,
            ccbeta = incoming.ccbeta,
            resvaluncert = incoming.resvaluncert,
            evallowlimit = incoming.evallowlimit,
            actionlevel = incoming.actionlevel,
            lmttyp_id = incoming.lmttyp_id,
            confirmation_sop = incoming.confirmation_sop,
            lu_s_productid = incoming.lu_s_productid,
            detailedcom = incoming.detailedcom,
            val_report_name = incoming.val_report_name,
            val_report_date = incoming.val_report_date,
            matrix_cal_curve = incoming.matrix_cal_curve,
            measuring_range = incoming.measuring_range,
            trueness_j_recovery = incoming.trueness_j_recovery,
            rsdr = incoming.rsdr,
            rsdwr_rsdrl = incoming.rsdwr_rsdrl,
            mutation_date = incoming.mutation_date,
            plan_nvwa_year = incoming.plan_nvwa_year,
            remarks = incoming.remarks,
            insert_date = incoming.insert_date
        FROM tmp_mctabel_save AS incoming
        WHERE incoming.sheetname = output.sheetname
          AND incoming.id = output.id
          AND ROW(output.team_id, output.groupori, output.use, output.productgroup_id, output.sample_matrix, output.e02_sampmatcode1_en, output.e02_sampmatcode1_nl, output.e02_sampmatcode2_en, output.e02_sampmatcode2_nl, output.e02_sampmatcode3_en, output.e02_sampmatcode3_nl, output.e02_sampmatcode4_en, output.e02_sampmatcode4_nl, output.mtx_id, output.substance_group, output.param_id, output.param_termextendedname, output.paramtext_lims, output.paramtext_abbreviation, output.paramtyp_id, output.anmethodref, output.flex_scope_no, output.qual_quan_method, output.anlytyp_id, output.anlymd_id, output.mdacc_id, output.resinfo, output.resunit_wfsr, output.unit_id, output.exprres_id, output.lod, output.loq, output.ccalpha, output.ccbeta, output.resvaluncert, output.evallowlimit, output.actionlevel, output.lmttyp_id, output.confirmation_sop, output.lu_s_productid, output.detailedcom, output.val_report_name, output.val_report_date, output.matrix_cal_curve, output.measuring_range, output.trueness_j_recovery, output.rsdr, output.rsdwr_rsdrl, output.mutation_date, output.plan_nvwa_year, output.remarks, output.insert_date)
              IS DISTINCT FROM
              ROW(incoming.team_id, incoming.groupori, incoming.use, incoming.productgroup_id, incoming.sample_matrix, incoming.e02_sampmatcode1_en, incoming.e02_sampmatcode1_nl, incoming.e02_sampmatcode2_en, incoming.e02_sampmatcode2_nl, incoming.e02_sampmatcode3_en, incoming.e02_sampmatcode3_nl, incoming.e02_sampmatcode4_en, incoming.e02_sampmatcode4_nl, incoming.mtx_id, incoming.substance_group, incoming.param_id, incoming.param_termextendedname, incoming.paramtext_lims, incoming.paramtext_abbreviation, incoming.paramtyp_id, incoming.anmethodref, incoming.flex_scope_no, incoming.qual_quan_method, incoming.anlytyp_id, incoming.anlymd_id, incoming.mdacc_id, incoming.resinfo, incoming.resunit_wfsr, incoming.unit_id, incoming.exprres_id, incoming.lod, incoming.loq, incoming.ccalpha, incoming.ccbeta, incoming.resvaluncert, incoming.evallowlimit, incoming.actionlevel, incoming.lmttyp_id, incoming.confirmation_sop, incoming.lu_s_productid, incoming.detailedcom, incoming.val_report_name, incoming.val_report_date, incoming.matrix_cal_curve, incoming.measuring_range, incoming.trueness_j_recovery, incoming.rsdr, incoming.rsdwr_rsdrl, incoming.mutation_date, incoming.plan_nvwa_year, incoming.remarks, incoming.insert_date);
    """

    insert_new_sql = """
        INSERT INTO mc.tabel_output (
            id, team_id, groupori, use, productgroup_id, sample_matrix, e02_sampmatcode1_en, e02_sampmatcode1_nl, e02_sampmatcode2_en, e02_sampmatcode2_nl, e02_sampmatcode3_en, e02_sampmatcode3_nl, e02_sampmatcode4_en, e02_sampmatcode4_nl, mtx_id, substance_group, param_id, param_termextendedname, paramtext_lims, paramtext_abbreviation, paramtyp_id, anmethodref, flex_scope_no, qual_quan_method, anlytyp_id, anlymd_id, mdacc_id, resinfo, resunit_wfsr, unit_id, exprres_id, lod, loq, ccalpha, ccbeta, resvaluncert, evallowlimit, actionlevel, lmttyp_id, confirmation_sop, lu_s_productid, detailedcom, val_report_name, val_report_date, matrix_cal_curve, measuring_range, trueness_j_recovery, rsdr, rsdwr_rsdrl, mutation_date, plan_nvwa_year, remarks, insert_date, sheetname
        )
        SELECT
            incoming.id, incoming.team_id, incoming.groupori, incoming.use, incoming.productgroup_id, incoming.sample_matrix, incoming.e02_sampmatcode1_en, incoming.e02_sampmatcode1_nl, incoming.e02_sampmatcode2_en, incoming.e02_sampmatcode2_nl, incoming.e02_sampmatcode3_en, incoming.e02_sampmatcode3_nl, incoming.e02_sampmatcode4_en, incoming.e02_sampmatcode4_nl, incoming.mtx_id, incoming.substance_group, incoming.param_id, incoming.param_termextendedname, incoming.paramtext_lims, incoming.paramtext_abbreviation, incoming.paramtyp_id, incoming.anmethodref, incoming.flex_scope_no, incoming.qual_quan_method, incoming.anlytyp_id, incoming.anlymd_id, incoming.mdacc_id, incoming.resinfo, incoming.resunit_wfsr, incoming.unit_id, incoming.exprres_id, incoming.lod, incoming.loq, incoming.ccalpha, incoming.ccbeta, incoming.resvaluncert, incoming.evallowlimit, incoming.actionlevel, incoming.lmttyp_id, incoming.confirmation_sop, incoming.lu_s_productid, incoming.detailedcom, incoming.val_report_name, incoming.val_report_date, incoming.matrix_cal_curve, incoming.measuring_range, incoming.trueness_j_recovery, incoming.rsdr, incoming.rsdwr_rsdrl, incoming.mutation_date, incoming.plan_nvwa_year, incoming.remarks, incoming.insert_date, incoming.sheetname
        FROM tmp_mctabel_save AS incoming
        WHERE NOT EXISTS (
            SELECT 1
            FROM mc.tabel_output AS output
            WHERE output.sheetname = incoming.sheetname
              AND output.id = incoming.id
        );
    """

    values = [(row.id, row.team_id, row.groupori, row.use, row.productgroup_id, row.sample_matrix, row.e02_sampmatcode1_en, row.e02_sampmatcode1_nl, row.e02_sampmatcode2_en, row.e02_sampmatcode2_nl, row.e02_sampmatcode3_en, row.e02_sampmatcode3_nl, row.e02_sampmatcode4_en, row.e02_sampmatcode4_nl, row.mtx_id, row.substance_group, row.param_id, row.param_termextendedname, row.paramtext_lims, row.paramtext_abbreviation, row.paramtyp_id, row.anmethodref, row.flex_scope_no, row.qual_quan_method, row.anlytyp_id, row.anlymd_id, row.mdacc_id, row.resinfo, row.resunit_wfsr, row.unit_id, row.exprres_id, row.lod, row.loq, row.ccalpha, row.ccbeta, row.resvaluncert, row.evallowlimit, row.actionlevel, row.lmttyp_id, row.confirmation_sop, row.lu_s_productid, row.detailedcom, row.val_report_name, row.val_report_date, row.matrix_cal_curve, row.measuring_range, row.trueness_j_recovery, row.rsdr, row.rsdwr_rsdrl, row.mutation_date, row.plan_nvwa_year, row.remarks, row.insert_date, row.sheetname) for row in rows]

    with PostgresDatabase(
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        realdictcursor=False,
    ) as db:
        try:
            db.execute(create_temp_sql)

            execute_values(
                db.cursor,
                insert_temp_sql,
                values,
                page_size=1000,
            )

            db.execute(lock_output_sql)

            db.execute(archive_sql)

            db.execute(update_existing_sql)
            updated_count = db.cursor.rowcount

            db.execute(insert_new_sql)
            inserted_count = db.cursor.rowcount

            db.commit()

        except Exception as exc:
            db.rollback()
            logger.exception("Failed to save mc.tabel data")
            raise HTTPException(
                status_code=500,
                detail="Failed to save table data.",
            ) from exc

    unchanged_count = len(rows) - updated_count - inserted_count

    return MCTabelSaveResponse(
        received=len(rows),
        inserted=inserted_count,
        updated=updated_count,
        unchanged=unchanged_count,
    )
