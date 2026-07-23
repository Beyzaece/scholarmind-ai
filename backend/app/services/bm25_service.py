from rank_bm25 import BM25Okapi

def tokenize_text(text: str) -> list[str]:
    return (
        text.lower()
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .replace(":", "")
        .replace(";", "")
        .split()
    )
def create_bm25_index(chunks: list[dict]):
    tokenized_chunks=[
        tokenize_text(chunk["text"])
        for chunk in chunks
    ]

    bm25=BM25Okapi(tokenized_chunks)
    return bm25

def search_bm25(
        question:str,
        chunks:list[dict],
        top_k:int=10
):
    if not chunks:
        return []
    bm25=create_bm25_index(chunks)
    tokenized_question=tokenize_text(question)
    scores=bm25.get_scores(tokenized_question)
    scored_chunks=[]
    for chunk,score in zip(chunks,scores):
        scored_chunk=chunk.copy()
        scored_chunk["bm25_score"]=float(score)
        scored_chunks.append(scored_chunk)
    scored_chunks.sort(
        key=lambda item: item["bm25_score"],
        reverse=True
    )
    return scored_chunks[:top_k]