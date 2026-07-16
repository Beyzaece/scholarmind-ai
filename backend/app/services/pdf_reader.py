import fitz
def extract_pages_from_pdf(file_bytes:bytes):
    doc=fitz.open(
        stream=file_bytes,
        filetype="pdf")
    pages=[]
    
    for page_number, page in enumerate(doc):
        page_text=page.get_text()
        pages.append({
            "page_number":page_number+1,
            "text":page_text
        })
        
    doc.close()
    return pages