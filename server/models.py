from pydantic import BaseModel

class Message(BaseModel):
    message_text: str
    is_incoming: bool
    conversation: str = None