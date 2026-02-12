from pydantic import BaseModel


class Gesture(BaseModel):
    """
    Represents the gesture + handedness.
    """
    gesture: str
    handedness: str

    def __eq__(self, other):
        return self.gesture == other.gesture and self.handedness == other.handedness

    def __hash__(self):
        return hash((self.gesture, self.handedness))
