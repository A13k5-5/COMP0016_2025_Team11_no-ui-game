from pydantic import BaseModel

class SerialNode(BaseModel):
    id: int
    text: str
    audio_path: str
    adjacency_list: dict[str, int]