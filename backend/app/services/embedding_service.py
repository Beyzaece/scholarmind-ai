from sentence_transformers import SentenceTransformer
model=SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)
def create_embeddings(chunks:list[str]):
    embeddings=model.encode(chunks)
    return embeddings

def create_query_embedding(question:str):
    embedding=model.encode([question])
    return embedding[0]