from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_pages_into_chunks(pages:list[dict]) -> list[dict]:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    all_chunks=[]

    for page in pages:
        page_chunks=splitter.split_text(page["text"])

        for chunk_index,chunk_text in enumerate (page_chunks):
            all_chunks.append({
                "page_number":page["page_number"],
                "chunk_index":chunk_index,
                "text":chunk_text
            })



    return all_chunks