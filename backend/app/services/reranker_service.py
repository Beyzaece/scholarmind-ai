from sentence_transformers import CrossEncoder
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L6-v2"
reranker_model=CrossEncoder(RERANKER_MODEL_NAME)


def rerank_chunks(
        question:str,
        chunks:list[dict],
        top_k:int=5
):
    if not chunks:
        return []
    question_chunk_pairs=[
        [question,chunk["text"]]
        for chunk in chunks
    ]

    scores=reranker_model.predict(question_chunk_pairs)

    for chunk,score in zip(chunks,scores):
        chunk["reranker_score"]=float(score)

    reranked_chunks=sorted(
        chunks,
        key=lambda chunk:chunk["reranker_score"],
        reverse=True
    )

    return reranked_chunks[:top_k]

