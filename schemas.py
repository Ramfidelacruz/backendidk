
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: str
    password: str

class PredictionBase(BaseModel):
    match_id: str
    home_score: int
    away_score: int

class PredictionCreate(PredictionBase):
    user_id: int
    created_at: datetime

class Prediction(PredictionBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class PasswordReset(BaseModel):
    email: str
    new_password: str