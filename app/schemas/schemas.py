from pydantic import BaseModel, EmailStr
from datetime import datetime

# ------------------- MC DATA
class MCdataIn(BaseModel):
    actionlevel:  float | None
    anlymd_code:  str
    anlymd_name:  str
    anlytyp_code:  str
    anlytyp_name:  str
    anmethodref:  str
    anmethodref_new:  str | None
    antibiotica_ab_groep:  str
    ccalpha:  float | None
    ccbeta:  float | None
    confirmation_sop:  str
    e02_sampmatcode1_en:  str
    e02_sampmatcode1_nl:  str
    e02_sampmatcode2_en:  str
    e02_sampmatcode2_nl:  str
    e02_sampmatcode3_en:  str | None
    e02_sampmatcode3_nl:  str | None
    e02_sampmatcode4_en:  str | None
    e02_sampmatcode4_nl:  str | None
    evallowlimit:  float | None
    exprres_code:  str
    flex_scope_no:  int
    groupori:  str | None
    identifier:  int
    insert_date:  datetime
    lmttyp_code:  str
    lmttyp_name:  str
    lod:  float | None
    loq:  float | None
    lu_s_productid:  str
    matrix_cal_curve:  str | None
    mdacc_code:  str
    mdacc_name:  str
    measuring_range:  str | None
    mtx_code:  str | None
    mutation_date:  datetime
    param_code:  str
    param_name:  str
    paramtext_abbreviation:  str | None
    paramtext_lims:  str
    paramtype_code:  str
    paramtype_name:  str
    plan_nvwa_year:  int
    productgroup:  str | None
    productmatrix_code:  str | None
    qual_quan_method:  str
    remarks:  str | None
    resinfo:  str | None
    resunit_wfsr:  str
    resvaluncert:  float | None
    rsdr:  float | None
    rsdwr_rsdrl:  float | None
    sample_matrix:  str
    substance_group:  str
    team_id:  int
    trueness_j_recovery:  float | None
    unit_code:  str
    use:  str
    val_report_date:  datetime
    val_report_name:  str


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

# --- Define the Pydantic model ---
class Person(BaseModel):
    firstname: str
    lastname: str
    age: int

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
