import uuid
from app.database.models import Conversation

def create_conversation(
        db,
        title:str,
        document_id:str |None=None
):
    conversation=Conversation(
        id=str(uuid.uuid4()),
        title=title,
        document_id=document_id
    )


    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_all_conversation(db):
    return(
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    
    )

def get_all_conversations(db):
    return(
    db.query(Conversation)
    .order_by(Conversation.created_at.desc())
    .all()
)