from enum import Enum

class EnumGesture(str, Enum):
    """
    Enum for the gestures. This is used to map the gesture to an integer for the adjacency list.
    """
    ILoveYou_Right = 0
    ILoveYou_Left = 1
    Victory_Left = 2
    Victory_Right = 3
    PointingUp_Right = 4
    PointingUp_Left = 5
    Closed_Fist_Right = 6
    Closed_Fist_Left = 7
    Open_Palm_Right = 8
    Open_Palm_Left = 9
    Thumb_Up_Right = 10
    Thumb_Up_Left = 11
    Thumb_Down_Right = 12
    Thumb_Down_Left = 13
    INVALID = None

    @staticmethod
    def from_gesture(gesture_category: str, handedness: str) -> 'EnumGesture':
        if gesture_category == "ILoveYou" and handedness == "Right":
            return EnumGesture.ILoveYou_Right
        elif gesture_category == "ILoveYou" and handedness == "Left":
            return EnumGesture.ILoveYou_Left
        elif gesture_category == "Victory" and handedness == "Left":
            return EnumGesture.Victory_Left
        elif gesture_category == "Victory" and handedness == "Right":
            return EnumGesture.Victory_Right
        elif gesture_category == "Pointing_Up" and handedness == "Right":
            return EnumGesture.PointingUp_Right
        elif gesture_category == "Pointing_Up" and handedness == "Left":
            return EnumGesture.PointingUp_Left
        elif gesture_category == "Closed_Fist" and handedness == "Right":
            return EnumGesture.Closed_Fist_Right
        elif gesture_category == "Closed_Fist" and handedness == "Left":
            return EnumGesture.Closed_Fist_Left
        elif gesture_category == "Open_Palm" and handedness == "Right":
            return EnumGesture.Open_Palm_Right
        elif gesture_category == "Open_Palm" and handedness == "Left":
            return EnumGesture.Open_Palm_Left
        elif gesture_category == "Thumb_Up" and handedness == "Right":
            return EnumGesture.Thumb_Up_Right
        elif gesture_category == "Thumb_Up" and handedness == "Left":
            return EnumGesture.Thumb_Up_Left
        elif gesture_category == "Thumb_Down" and handedness == "Right":
            return EnumGesture.Thumb_Down_Right
        else:
            return EnumGesture.INVALID
