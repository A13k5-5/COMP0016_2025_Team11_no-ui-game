from enum import Enum

class EnumGesture(str, Enum):
    """
    Enum for the gestures. This is used to map the gesture to an integer for the adjacency list.
    """
    ILoveYou_Right = 0
    ILoveYou_Left = 1
    INVALID = None

    @staticmethod
    def from_gesture(gesture_category: str, handedness: str) -> 'EnumGesture':
        if gesture_category == "ILoveYou" and handedness == "Right":
            return EnumGesture.ILoveYou_Right
        elif gesture_category == "ILoveYou" and handedness == "Left":
            return EnumGesture.ILoveYou_Left
        else:
            return EnumGesture.INVALID
