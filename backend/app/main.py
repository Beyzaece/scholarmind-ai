from fastapi import FastAPI,UploadFile,File
from app.services.pdf_reader import extract_text_from_pdf
from app.services.text_chunker import split_text_into_chunks

from pydantic import BaseModel
from app.services.vector_store import ( store_chunks,search_similar_chunks)
from app.services.embedding_service import (
    create_embeddings,create_query_embedding
)

class QuestionRequest(BaseModel):
    question: str

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
async def upload_pdf(file:UploadFile=File(...)):

    text=extract_text_from_pdf(file.file)
    chunks=split_text_into_chunks(text)
    embeddings=create_embeddings(chunks)
    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=file.filename
    )
    return{
        "filename":file.filename,
        "character":len(text),
       
        "chunk_count":len(chunks),
        "first_chunk":chunks[0] if chunks else "",
        "embedding_dimension": len(embeddings[0]) if len(embeddings) > 0 else 0,
        "stored":True
        
    }

@app.post("/search")
def search_chunks(request:QuestionRequest):
    query_embeddings=create_query_embedding(request.question)
    results=search_similar_chunks(query_embedding=query_embeddings,
                                 n_results=3)
    
    return {
        "question": request.question,
        "documents": results["documents"][0],
        "metadatas": results["metadatas"][0],
        "distances": results["distances"][0]
    }
