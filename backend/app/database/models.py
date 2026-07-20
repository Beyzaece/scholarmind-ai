from datetime import datetime,UTC
from sqlalchemy import Column,DateTime,Integer,String
from app.database.database import Base
from sqlalchemy import ForeignKey,Text
from sqlalchemy.orm import relationship
from app.database.database import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

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
class Conversation(Base):
    __tablename__="conversations"

    id=Column(
        String,
        primary_key=True,
        index=True)
    
    title=Column(
        String,
        nullable=False
    )
    document_id=Column(
        String,
        nullable=True
    )
    created_at=Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    messages=relationship(
        "Message",
        back_populates="conversation",
        cascade="all,delete-orphan"
    )
class Message(Base):
    __tablename__="messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    conversation_id = Column(
        String,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )
