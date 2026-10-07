from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="employee")

    documents = relationship("Document", back_populates="uploader")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    department = Column(String, nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    uploader = relationship("User", back_populates="documents")