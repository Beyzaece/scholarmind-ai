

from app.database.models import Message


def create_message(
    db,
    conversation_id: str,
    role: str,
    content: str
):
    message = Message(
        
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message

def get_conversation_messages(
        db,
        conversation_id:str
):
    return(
        db.query(Message)
        .filter(Message.conversation_id==conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )