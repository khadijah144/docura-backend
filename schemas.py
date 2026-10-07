from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------- AUTH ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ---------- USERS ----------

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


# ---------- DOCUMENTS ----------

class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    department: str
    uploaded_by: int
    upload_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- SEARCH ----------

class SearchRequest(BaseModel):
    query: str


class SearchResult(BaseModel):
    id: int
    title: str
    filename: str
    department: str
    uploaded_by: int
    upload_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- AI / RAG ----------

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str