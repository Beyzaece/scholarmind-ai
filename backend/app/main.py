from fastapi import FastAPI, Depends, File, UploadFile,HTTPException
from app.services.pdf_reader import extract_pages_from_pdf
from app.services.text_chunker import split_pages_into_chunks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.vector_store import (
    store_chunks,
    delete_document_chunks
)
from google.genai.errors import ServerError
from app.services.embedding_service import create_embeddings
from app.services.document_service import (generate_document_id,generate_file_hash,document_exists)
from app.database.database import Base,engine,get_db
from app.database import models
from app.database.models import Document
from sqlalchemy.orm import Session
from app.services.conversation_service import create_conversation,get_all_conversation
from app.services.message_service import (
     create_message,
     get_conversation_messages)
from app.services.retrieval_service import retrieve_relevant_chunks
class QuestionRequest(BaseModel):
    question: str
    document_id: str | None = None
    conversation_id:str | None=None
from app.services.response_service import build_sources
from app.services.answer_service import generate_answer_with_retry

Base.metadata.create_all(bind=engine)
app=FastAPI(
    title="ScholarMind AI",
    description="RAG-based AI Researcher Assistant",
    version="1.0.0"

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversationCreateRequest(BaseModel):
    title:str
    document_id:str | None=None

@app.get("/")
def root():
    return{"message":"Welcome to ScholarMınd AI"}
@app.get("/health")
def health_check():
    return{
        "status":"ok",
        "message":"ScholarMind AI backend is running"
    }
@app.post("/upload")
async def upload_pdf(file:UploadFile=File(...),
                     db:Session=Depends(get_db)):

    file_bytes=await file.read()
    file_hash=generate_file_hash(file_bytes)

    if document_exists(file_hash):
        return{
            "stored":False,
            "message":"Bu döküman zaten mevcut"
        }
    document_id=generate_document_id()

    pages=extract_pages_from_pdf(file_bytes)
    chunks=split_pages_into_chunks(pages)
    

    chunk_texts=[chunk["text"] for chunk in chunks]
    embeddings=create_embeddings(chunk_texts)

    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=file.filename,
        document_id=document_id,
        file_hash=file_hash
    )
    document=Document(
        id=document_id,
        filename=file.filename,
        file_hash=file_hash,
        page_count=len(pages)
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    total_character=sum(len(page["text"]) for page in pages)

    return{
        "document_id": document_id,
        "file_hash": file_hash,
        "filename":file.filename,
        "page_count":len(pages),
        "character_count":total_character,
       
        "chunk_count":len(chunks),
        "first_chunk":chunks[0] if chunks else "",
        "embedding_dimension": len(embeddings[0]) if len(embeddings) > 0 else 0,
        "stored":True
        
    }

@app.get("/documents")
def get_documents(
    db:Session=Depends(get_db)
):
    documents=db.query(Document).order_by(
        Document.uploaded_at.desc()
    ).all()
    return[
        {
            "document_id": document.id,
            "filename": document.filename,
            "page_count": document.page_count,
            "uploaded_at": document.uploaded_at

        }
        for document in documents
    ]

@app.delete("/documents/{document_id}")
def delete_document(
    document_id:str,
    db:Session=Depends(get_db)

):
    document=db.query(Document).filter(
        Document.id==document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Döküman bulunamadı"
        )
    try:
        delete_document_chunks(document_id)
        db.delete(document)
        db.commit()

        return {
            "deleted": True,
            "document_id": document_id,
            "message": f"{document.filename} başarıyla silindi."
        }
    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Doküman silinirken hata oluştu: {str(error)}"
        )


@app.post("/search")
def search_chunks(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    if request.conversation_id:
        create_message(
            db=db,
            conversation_id=request.conversation_id,
            role="user",
            content=request.question
        )

    diverse_results = retrieve_relevant_chunks(
        question=request.question,
        document_id=request.document_id
    )

    relevant_chunks = [
        item["text"]
        for item in diverse_results
    ]

    if not relevant_chunks:
        answer = (
            "Bu soruyla ilgili yeterince alakalı "
            "bir kaynak bulunamadı."
        )

        if request.conversation_id:
            create_message(
                db=db,
                conversation_id=request.conversation_id,
                role="assistant",
                content=answer
            )

        return {
            "question": request.question,
            "answer": answer,
            "sources": [],
            "conversation_id": request.conversation_id
        }

    try:
        answer = generate_answer_with_retry(
            question=request.question,
            context_chunks=relevant_chunks
        )

    except ServerError:
        raise HTTPException(
            status_code=503,
            detail="Yapay zeka servisi şu anda yoğun."
        )

    if request.conversation_id:
        create_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer
        )

    sources = build_sources(diverse_results)

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
        "conversation_id": request.conversation_id
    }
@app.post("/conversations")
def create_new_conversation(
    request: ConversationCreateRequest,
    db:Session=Depends(get_db)
):
    conversation= create_conversation(
        db=db,
        title=request.title,
        document_id=request.document_id
    )

    return{
        "conversation_id":conversation.id,
        "title":conversation.title,
        "document_id":conversation.document_id,
        "created_at":conversation.created_at
        
    }
@app.get("/conversations")
def list_conversations(
    db:Session=Depends(get_db)):

    conversations=get_all_conversation(db)
    return[
        {
            "conversation_id":conversation.id,
            "title":conversation.title,
            "document_id":conversation.document_id,
            "created_at":conversation.created_at
        }
        for conversation in conversations
    ]

@app.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id:str,
    db:Session=Depends(get_db)
):
    messages=get_conversation_messages(
        db=db,
        conversation_id=conversation_id
    )
    return[
        {
            "id":message.id,
            "role":message.role,
            "content":message.content,
            "created_at":message.created_at
        }
        for message in messages
    ]