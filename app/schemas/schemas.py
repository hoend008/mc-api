from pydantic import BaseModel, EmailStr
from datetime import datetime


##### schemas for validating data from user

# schema for validation countries
class Country(BaseModel):
    id: int
    code2: str
    code3: str
    country: str

# schema for validation samples
class Sample(BaseModel):
    id: int
    dataprovider: str
    sample_number: str
    country_id: int
    feedconversion_id: int

# schema for validation counts
class Count(BaseModel):
    count: int

# schema for validation year, counts
class SampleYears(BaseModel):
    year: int
    count: int

class SampleCountry(BaseModel):
    id: str
    value: int

# schema for validation predictions
class Prediction(BaseModel):
    code3: str
    value: float

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
