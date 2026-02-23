from pydantic import BaseModel

from gesture import EnumGesture


class SerialNode(BaseModel):
    id: int
    text: str
    left_option: str = ""
    right_option: str = ""
    audio_filename: str
    adjacency_list: dict[EnumGesture, int]
    is_win: bool = False
