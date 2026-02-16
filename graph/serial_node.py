from pydantic import BaseModel

from gesture import EnumGesture


class SerialNode(BaseModel):
    id: int
    text: str
    audio_path: str
    adjacency_list: dict[EnumGesture, int]
