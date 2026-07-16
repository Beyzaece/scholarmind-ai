from fastapi import FastAPI, Depends, File, UploadFile,HTTPException
from app.services.pdf_reader import extract_pages_from_pdf
from app.services.text_chunker import split_pages_into_chunks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.vector_store import ( store_chunks,search_similar_chunks,delete_document_chunks)
from app.services.embedding_service import (
    create_embeddings,create_query_embedding
)
from app.services.document_service import (generate_document_id,generate_file_hash,document_exists)
from app.services.llm_services import generate_answer
from app.database.database import Base,engine,get_db
from app.database import models
from app.database.models import Document
from sqlalchemy.orm import Session
from fastapi import HTTPException

class QuestionRequest(BaseModel):
    question: str
    document_id: str | None = None
Base.metadata.create_all(bind=engine)
app=FastAPI(
    title="ScholarMind AI",
    description="RAG-based AI Researcher Assistant",
    version="1.0.0"

)
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
def get_comments(
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
def search_chunks(request:QuestionRequest):
    query_embeddings=create_query_embedding(request.question)
    results=search_similar_chunks(query_embedding=query_embeddings,
                                 n_results=3,
                                 document_id=request.document_id)
    
    relevant_chunks=results["documents"][0]
    answer=generate_answer(question=request.question,
                           context_chunks=relevant_chunks)
    
    return {
        "question": request.question,
        "answer": answer,
        "sources": results["metadatas"][0],
        "distances": results["distances"][0]
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)