import cv2
import time
import math
from mediapipe.tasks import python
from mediapipe.tasks.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    PoseLandmarker,
    PoseLandmarkerOptions,
    VisionRunningMode
)

# --- CONFIG ---
HOLD_TIME = 2.0
CAMERA_INDEX = 0

# --- UTILS ---
def euclidean_distance(lm1, lm2):
    return math.sqrt((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)

# --- STATE ---
hand_raised_start = None

# --- MODEL PATHS ---
hand_model_path = "hand_landmarker.task"
pose_model_path = "pose_landmarker_full.task"

# --- MEDIA PIPE SETUP ---
hand_options = HandLandmarkerOptions(
    model_asset_path=hand_model_path,
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_hand_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
hand_landmarker = HandLandmarker.create_from_options(hand_options)

pose_options = PoseLandmarkerOptions(
    model_asset_path=pose_model_path,
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_pose_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
pose_landmarker = PoseLandmarker.create_from_options(pose_options)

# --- CAMERA ---
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise RuntimeError("Could not open camera")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    timestamp = int(time.time() * 1000)

    # Convert frame to MediaPipe Image
    mp_image = python.Image(
        image_format=python.ImageFormat.SRGB,
        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )

    # --- POSE ---
    pose_result = pose_landmarker.recognize_async(mp_image, timestamp)
    main_person_bbox = None

    if pose_result.pose_landmarks:
        # pick first person detected
        landmarks = pose_result.pose_landmarks[0].landmarks
        left_shoulder = landmarks[11]   # LEFT_SHOULDER
        right_shoulder = landmarks[12]  # RIGHT_SHOULDER

        cx = (left_shoulder.x + right_shoulder.x) / 2
        cy = (left_shoulder.y + right_shoulder.y) / 2
        size = euclidean_distance(left_shoulder, right_shoulder)
        main_person_bbox = (cx, cy, size)

        # Draw simple pose (just shoulders)
        cv2.circle(frame, (int(left_shoulder.x*w), int(left_shoulder.y*h)), 5, (255,0,0), -1)
        cv2.circle(frame, (int(right_shoulder.x*w), int(right_shoulder.y*h)), 5, (255,0,0), -1)
        cv2.line(frame,
                 (int(left_shoulder.x*w), int(left_shoulder.y*h)),
                 (int(right_shoulder.x*w), int(right_shoulder.y*h)),
                 (255,0,0), 2)

    # --- HANDS ---
    hand_result = hand_landmarker.recognize_async(mp_image, timestamp)
    interaction_confirmed = False

    if hand_result.hand_landmarks and main_person_bbox:
        cx, cy, size = main_person_bbox

        for hand_landmarks in hand_result.hand_landmarks:
            wrist = hand_landmarks[0]         # WRIST
            middle_mcp = hand_landmarks[9]    # MIDDLE_FINGER_MCP

            # check hand near main person
            if abs(wrist.x - cx) < size and abs(wrist.y - cy) < size:
                wrist_y = int(wrist.y * h)
                middle_mcp_y = int(middle_mcp.y * h)

                # hand raised logic
                if wrist_y < middle_mcp_y:
                    if hand_raised_start is None:
                        hand_raised_start = time.time()
                    elif time.time() - hand_raised_start >= HOLD_TIME:
                        interaction_confirmed = True
                else:
                    hand_raised_start = None
    else:
        hand_raised_start = None

    # --- DISPLAY ---
    if interaction_confirmed:
        cv2.putText(frame, "INTERACTION STARTED", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
    elif hand_raised_start is not None:
        elapsed = time.time() - hand_raised_start
        cv2.putText(frame, f"HOLDING... {elapsed:.1f}s", (40,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,255), 2)

    cv2.imshow("Hand Raise Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()