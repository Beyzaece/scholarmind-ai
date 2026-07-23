import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="scholarmind_documents"
)
def store_chunks(
    chunks: list[dict],
    embeddings,
    filename: str,
    document_id: str,
    file_hash: str
) -> None:

    ids = [
        f"{document_id}-page-{chunk['page_number']}-chunk-{chunk['chunk_index']}"
        for chunk in chunks
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_id": document_id,
            "file_hash": file_hash,
            "filename": filename,
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )
def delete_document_chunks(document_id: str) -> None:
    collection.delete(
        where={
            "document_id": document_id
        }
    )

def search_similar_chunks(
    query_embedding,
    n_results: int = 3,
    document_id: str | None=None
):
    
    if document_id:
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where={
                "document_id":document_id
            }
        )
    else:
        results=collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )

    return results


def find_document_by_hash(file_hash:str):
    results=collection.get(
        where={"file_hash":file_hash},
        limit=1

    )
    return results
def get_all_chunks(
    document_id: str | None = None
) -> list[dict]:

    where_filter = None

    if document_id:
        where_filter = {
            "document_id": document_id
        }

    results = collection.get(
        where=where_filter,
        include=[
            "documents",
            "metadatas"
        ]
    )

    chunks = []

    for document, metadata in zip(
        results["documents"],
        results["metadatas"]
    ):
        chunks.append({
            "text": document,
            "metadata": metadata
        })

    return chunks