def build_sources(chunks: list[dict]) -> list[dict]:
    sources = []

    for item in chunks:
        metadata = item["metadata"]

        sources.append({
            "filename": metadata.get("filename"),
            "page_number": metadata.get("page_number"),
            "chunk_index": metadata.get("chunk_index"),
            "text": item["text"],
            "distance": item.get("distance"),
            "bm25_score": item.get("bm25_score"),
            "rrf_score": item.get("rrf_score"),
            "reranker_score": item.get("reranker_score")
        })

    return sources