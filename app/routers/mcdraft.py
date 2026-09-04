from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import Json, execute_values

from DB.PostgresDatabasev2 import PostgresDatabase
from DB.DBcredentials import DB_USER, DB_PASSWORD, DB_NAME
from schemas.schemas import (
    MCDraftDeleteResponse,
    MCDraftOut,
    MCDraftSaveRequest,
    MCDraftSaveResponse,
    MCDraftSummary,
    UserInDB,
)
from utils.oauth2 import get_current_user


router = APIRouter(
    prefix="/mcdraft",
    tags=["mc drafts"],
)


@router.get("", response_model=List[MCDraftSummary])
def list_drafts(
    current_user: UserInDB = Depends(get_current_user),
):
    query = """
        SELECT
            d.draft_id,
            d.sheetname,
            d.created_at,
            d.updated_at,
            COUNT(r.draft_row_id)::int AS row_count
        FROM mc.tabel_draft AS d
        LEFT JOIN mc.tabel_draft_row AS r
            ON r.draft_id = d.draft_id
        WHERE d.user_id = %s
        GROUP BY
            d.draft_id,
            d.sheetname,
            d.created_at,
            d.updated_at
        ORDER BY d.updated_at DESC;
    """

    with PostgresDatabase(
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        realdictcursor=True,
    ) as db:
        db.execute(query, (current_user.id,))
        rows = db.fetchall()

    return rows


@router.get("/{sheetname}", response_model=MCDraftOut)
def get_draft(
    sheetname: str,
    current_user: UserInDB = Depends(get_current_user),
):
    draft_query = """
        SELECT
            draft_id,
            user_id,
            sheetname,
            created_at,
            updated_at
        FROM mc.tabel_draft
        WHERE user_id = %s
          AND sheetname = %s;
    """

    rows_query = """
        SELECT
            draft_row_id,
            id,
            row_position,
            current_data,
            baseline_data
        FROM mc.tabel_draft_row
        WHERE draft_id = %s
        ORDER BY row_position;
    """

    with PostgresDatabase(
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        realdictcursor=True,
    ) as db:
        db.execute(draft_query, (current_user.id, sheetname))
        draft = db.fetchone()

        if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No saved draft exists for this sheet.",
            )

        db.execute(rows_query, (draft["draft_id"],))
        draft_rows = db.fetchall()

    return {
        **draft,
        "rows": draft_rows,
    }


@router.post("", response_model=MCDraftSaveResponse)
def save_draft(
    payload: MCDraftSaveRequest,
    current_user: UserInDB = Depends(get_current_user),
):
    if not payload.sheetname.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sheetname may not be empty.",
        )

    row_ids = [row.id for row in payload.rows]
    if len(row_ids) != len(set(row_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The draft contains duplicate row ids.",
        )

    row_positions = [row.row_position for row in payload.rows]
    if len(row_positions) != len(set(row_positions)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The draft contains duplicate row positions.",
        )

    upsert_draft_query = """
        INSERT INTO mc.tabel_draft (
            user_id,
            sheetname
        )
        VALUES (%s, %s)
        ON CONFLICT (user_id, sheetname)
        DO UPDATE SET
            updated_at = CURRENT_TIMESTAMP
        RETURNING
            draft_id,
            sheetname,
            updated_at;
    """

    delete_old_rows_query = """
        DELETE FROM mc.tabel_draft_row
        WHERE draft_id = %s;
    """

    insert_rows_query = """
        INSERT INTO mc.tabel_draft_row (
            draft_id,
            id,
            row_position,
            current_data,
            baseline_data
        )
        VALUES %s;
    """

    with PostgresDatabase(
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        realdictcursor=True,
    ) as db:
        try:
            db.execute(
                upsert_draft_query,
                (current_user.id, payload.sheetname),
            )
            draft = db.fetchone()
            draft_id = draft["draft_id"]

            db.execute(delete_old_rows_query, (draft_id,))

            if payload.rows:
                values = [
                    (
                        draft_id,
                        row.id,
                        row.row_position,
                        Json(row.current_data),
                        Json(row.baseline_data),
                    )
                    for row in payload.rows
                ]

                execute_values(
                    db.cursor,
                    insert_rows_query,
                    values,
                    page_size=1000,
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

    return MCDraftSaveResponse(
        draft_id=draft_id,
        sheetname=draft["sheetname"],
        row_count=len(payload.rows),
        updated_at=draft["updated_at"],
    )


@router.delete("/{sheetname}", response_model=MCDraftDeleteResponse)
def delete_draft(
    sheetname: str,
    current_user: UserInDB = Depends(get_current_user),
):
    query = """
        DELETE FROM mc.tabel_draft
        WHERE user_id = %s
          AND sheetname = %s
        RETURNING draft_id;
    """

    with PostgresDatabase(
        DB_NAME,
        DB_USER,
        DB_PASSWORD,
        realdictcursor=False,
    ) as db:
        db.execute(query, (current_user.id, sheetname))
        deleted = db.fetchone() is not None

    return MCDraftDeleteResponse(
        deleted=deleted,
        sheetname=sheetname,
    )
