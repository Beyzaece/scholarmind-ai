from datetime import datetime,UTC
from sqlalchemy import Column,DateTime,Integer,String
from app.database.database import Base

class Document(Base):
    __tablename__="documents"
    id=Column(
        String,
        primary_key=True,
        index=True
    )
    filename=Column(
        String,
        nullable=False
    )

    file_hash=Column(String,
                     nullable=False,
                     unique=True)
    page_count=Column(
        Integer,
        nullable=False

    )

    uploaded_at=Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )
