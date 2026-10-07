from pathlib import Path
import uuid
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import Base, SessionLocal, engine, get_db
from models import Document, User
from schemas import (
    AskRequest,
    AskResponse,
    DocumentResponse,
    LoginRequest,
    SearchRequest,
    SearchResult,
    TokenResponse,
    UserResponse,
)


# ---------- DATABASE ----------

Base.metadata.create_all(bind=engine)
def create_demo_users():
    db = SessionLocal()

    try:
        if not db.query(User).filter(User.username == "hr").first():
            hr_user = User(
                username="hr",
                password_hash=hash_password("hr12345"),
                role="hr",
            )
            db.add(hr_user)

        if not db.query(User).filter(User.username == "employee").first():
            employee_user = User(
                username="employee",
                password_hash=hash_password("employee123"),
                role="employee",
            )
            db.add(employee_user)

        db.commit()

    finally:
        db.close()


create_demo_users()

# ---------- APP ----------

app = FastAPI(
    title="Docura API",
    description="Document handling and AI-powered document search system",
    version="1.0.0",
)


# ---------- CORS ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- FILE STORAGE ----------

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".jpeg",
    ".jpg",
    ".png",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ---------- DEPARTMENTS ----------

DEPARTMENTS = {
    "Operations",
    "Finance",
    "HR",
    "Engineering/IT",
    "Marketing",
    "Sales",
}


# ---------- BASIC ROUTE ----------

@app.get("/")
def root():
    return {
        "message": "Docura API is running",
        "docs": "/docs",
    }


# ---------- AUTH ----------

@app.post("/auth/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == login_data.username)
        .first()
    )

    if not user or not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ---------- CURRENT USER ----------

@app.get("/auth/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ---------- DOCUMENT UPLOAD ----------

@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    title: str,
    department: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if department not in DEPARTMENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid department",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required",
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Supported types: PDF, DOCX, TXT, MD, JPEG, JPG, PNG",
        )

    file_content = file.file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty",
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size cannot exceed 10 MB",
        )

    unique_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        buffer.write(file_content)

    document = Document(
        title=title,
        filename=original_filename,
        file_path=str(file_path),
        department=department,
        uploaded_by=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

# ---------- LIST DOCUMENTS ----------

@app.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    department: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Document)

    if department:
        if department not in DEPARTMENTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department",
            )

        query = query.filter(Document.department == department)

    return query.order_by(Document.upload_date.desc()).all()


# ---------- GET DOCUMENT ----------

@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


# ---------- DELETE DOCUMENT ----------

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Only HR or the person who uploaded the document can delete it.
    if (
        current_user.role != "hr"
        and document.uploaded_by != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this document",
        )

    file_path = Path(document.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }


# ---------- SEARCH ----------

@app.post("/search", response_model=list[SearchResult])
def search_documents(
    search_data: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = search_data.query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    search_pattern = f"%{query}%"

    results = (
        db.query(Document)
        .filter(
            (Document.title.ilike(search_pattern))
            | (Document.filename.ilike(search_pattern))
            | (Document.department.ilike(search_pattern))
        )
        .order_by(Document.upload_date.desc())
        .all()
    )

    return results


# ---------- AI / RAG INTEGRATION POINT ----------

# AI/RAG INTEGRATION POINT
# AI TEAM WORKS HERE.
#
# This endpoint is intentionally simple for now.
# The AI teammate can replace the placeholder logic
# with document retrieval + RAG + answer generation.
#
# Do not modify authentication, database models,
# document storage, or unrelated backend logic
# while integrating the RAG system.

@app.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    current_user: User = Depends(get_current_user),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty",
        )

    return {
        "answer": (
            "RAG integration is not connected yet. "
            "The AI team should implement document retrieval "
            "and answer generation here."
        )
    }