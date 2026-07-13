import chromadb
client=chromadb.PersistentClient(path="./chroma_db")

collection=client.get_or_create_collection(
    name="scholarmind_documents"
)

def store_chunks(
    chunks:list[str],
    embeddings,
    filename:str
) -> None:
    ids=[
        f"{filename}-chunk-{index}"
        for index in range(len(chunks))
    ]

    metadatas=[{
        "filename":filename,
        "chunk_index":index
        }
        for index in range(len(chunks))

    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas

    )

def search_similar_chunks(
        query_embedding,
        n_results:int=3

):
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results