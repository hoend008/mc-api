from pydantic import BaseModel, EmailStr
from datetime import datetime

# ------------------- MC DATA
class MCdata(BaseModel):
    team_id: int
    identifier: int
    mutation_date: datetime
    insert_date: datetime
    val_report_name: str
    val_report_date: datetime
    plan_nvwa_year: int
    groupori: str
    use: str
    productgroup: str
    sample_matrix: str
    e02_sampmatcode1_en: str
    e02_sampmatcode1_nl: str
    e02_sampmatcode2_en: str
    e02_sampmatcode2_nl: str
    e02_sampmatcode3_en: str
    e02_sampmatcode3_nl: str
    e02_sampmatcode4_en: str
    e02_sampmatcode4_nl: str
    productmatrix_code: str
    mtx_code: str
    substance_group: str
    antibiotica_ab_groep: str
    param_code: str
    param_name: str
    paramtext_lims: str
    paramtext_abbreviation: str
    paramtype_code: str
    paramtype_name: str
    anmethodref: str
    anmethodref_new: str
    flex_scope_no: int
    qual_quan_method: str
    anlytyp_code: str
    anlytyp_name: str
    anlymd_code: str
    anlymd_name: str
    mdacc_code: str
    mdacc_name: str
    resinfo: str
    resunit_wfsr: str
    unit_code: str
    exprres_code: str
    lod: float | None
    loq: float | None
    ccalpha: float | None
    ccbeta: float | None
    resvaluncert: float | None
    evallowlimit: float | None
    actionlevel: float | None
    lmttyp_code: str
    lmttyp_name: str
    confirmation_sop: str
    lu_s_productid: str
    matrix_cal_curve: str
    measuring_range: str
    trueness_j_recovery: float | None
    rsdr: float | None
    rsdwr_rsdrl: float | None
    remarks: str

class MCdataOut(BaseModel):
    id: int
    team_id: int
    identifier: int
    mutation_date: datetime
    insert_date: datetime
    val_report_name: str
    val_report_date: datetime
    plan_nvwa_year: int
    groupori: str
    use: str
    productgroup: str
    sample_matrix: str
    e02_sampmatcode1_en: str
    e02_sampmatcode1_nl: str
    e02_sampmatcode2_en: str
    e02_sampmatcode2_nl: str
    e02_sampmatcode3_en: str
    e02_sampmatcode3_nl: str
    e02_sampmatcode4_en: str
    e02_sampmatcode4_nl: str
    productmatrix_code: str
    mtx_code: str
    substance_group: str
    antibiotica_ab_groep: str
    param_code: str
    param_name: str
    paramtext_lims: str
    paramtext_abbreviation: str
    paramtype_code: str
    paramtype_name: str
    anmethodref: str
    anmethodref_new: str
    flex_scope_no: int
    qual_quan_method: str
    anlytyp_code: str
    anlytyp_name: str
    anlymd_code: str
    anlymd_name: str
    mdacc_code: str
    mdacc_name: str
    resinfo: str
    resunit_wfsr: str
    unit_code: str
    exprres_code: str
    lod: float | None
    loq: float | None
    ccalpha: float | None
    ccbeta: float | None
    resvaluncert: float | None
    evallowlimit: float | None
    actionlevel: float | None
    lmttyp_code: str
    lmttyp_name: str
    confirmation_sop: str
    lu_s_productid: str
    matrix_cal_curve: str
    measuring_range: str
    trueness_j_recovery: float | None
    rsdr: float | None
    rsdwr_rsdrl: float | None
    remarks: str
    created_at: datetime

class ReturnMessage(BaseModel):
    msg: str

# ------------------- USERS
# Schema for validating user creation
class UserCreate(BaseModel):
    username: str
    hashed_password: str
    
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    created_at: datetime

    
##### schemas for validation user authentication info
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str
