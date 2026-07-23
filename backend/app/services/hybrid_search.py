def reciprocal_rank_fusion(
    embedding_results: list[dict],
    bm25_results: list[dict],
    k: int = 60
) -> list[dict]:
    fused_results = {}

    for rank, item in enumerate(embedding_results, start=1):
        metadata = item["metadata"]

        chunk_key = (
            metadata.get("document_id"),
            metadata.get("page_number"),
            metadata.get("chunk_index")
        )

        if chunk_key not in fused_results:
            fused_results[chunk_key] = item.copy()
            fused_results[chunk_key]["rrf_score"] = 0.0

        fused_results[chunk_key]["rrf_score"] += (
            1 / (k + rank)
        )

        ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return ranked_results