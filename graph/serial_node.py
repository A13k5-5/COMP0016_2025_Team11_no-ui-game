from pydantic import BaseModel

from gesture import Gesture


class SerialNode(BaseModel):
    id: int
    text: str
    audio_path: str
    adjacency_list: dict[Gesture, int]
