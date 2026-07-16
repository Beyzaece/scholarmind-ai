import uuid 
import hashlib
from app.services.vector_store import find_document_by_hash

def generate_document_id():
    return str(uuid.uuid4())


def generate_file_hash(file_bytes:bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def document_exists(file_hash:str)->bool:
    results=find_document_by_hash(file_hash)

    return len(results["ids"])