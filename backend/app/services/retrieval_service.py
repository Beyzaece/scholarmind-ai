from app.services.embedding_service import create_query_embedding
from app.services.vector_store import (
    search_similar_chunks,
    get_all_chunks
)
from app.services.bm25_service import search_bm25
from app.services.hybrid_search import reciprocal_rank_fusion
from app.services.reranker_service import rerank_chunks
from app.services.llm_services import generate_search_queries
from google.genai.errors import ClientError

def retrieve_relevant_chunks(
    question: str,
    document_id: str | None = None,
    embedding_top_k: int = 10,
    bm25_top_k: int = 10,
    final_top_k: int = 3
) -> list[dict]:

    try:
        queries = generate_search_queries(
            question=question
        )
    except Exception:
        queries = [question]

    print("=" * 50)
    print("Generated Queries")
    print(queries)
    print("=" * 50)

    all_chunks = get_all_chunks(
        document_id=document_id
    )

    embedding_results = []
    bm25_results = []

    for query in queries:
        query_embedding = create_query_embedding(query)

        results = search_similar_chunks(
            query_embedding=query_embedding,
            n_results=embedding_top_k,
            document_id=document_id
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            if distance <= 1.3:
                embedding_results.append({
                    "text": document,
                    "metadata": metadata,
                    "distance": distance
                })

        query_bm25_results = search_bm25(
            question=query,
            chunks=all_chunks,
            top_k=bm25_top_k
        )

        bm25_results.extend(query_bm25_results)

    unique_embedding_results = []
    seen_embedding = set()

    for item in embedding_results:
        metadata = item["metadata"]

        key = (
            metadata.get("document_id"),
            metadata.get("page_number"),
            metadata.get("chunk_index")
        )

        if key not in seen_embedding:
            unique_embedding_results.append(item)
            seen_embedding.add(key)

    unique_bm25_results = []
    seen_bm25 = set()

    for item in bm25_results:
        metadata = item["metadata"]

        key = (
            metadata.get("document_id"),
            metadata.get("page_number"),
            metadata.get("chunk_index")
        )

        if key not in seen_bm25:
            unique_bm25_results.append(item)
            seen_bm25.add(key)

    hybrid_results = reciprocal_rank_fusion(
        embedding_results=unique_embedding_results,
        bm25_results=unique_bm25_results
    )

    reranked_results = rerank_chunks(
        question=question,
        chunks=hybrid_results,
        top_k=len(hybrid_results)
    )

    diverse_results = []
    used_pages = set()

    for item in reranked_results:
        metadata = item["metadata"]

        page_key = (
            metadata.get("document_id"),
            metadata.get("page_number")
        )

        if page_key not in used_pages:
            diverse_results.append(item)
            used_pages.add(page_key)

        if len(diverse_results) == final_top_k:
            break

    return diverse_results