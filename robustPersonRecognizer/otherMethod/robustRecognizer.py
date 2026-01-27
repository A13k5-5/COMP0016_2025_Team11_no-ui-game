import cv2
import time
import mediapipe as mp
import math

# ---------------- CONFIG ----------------
HOLD_TIME = 2.0  # seconds hand must be held up
CAMERA_INDEX = 0

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ---------------- STATE ----------------
hand_raised_start = None

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise RuntimeError("Could not open camera")

print("Press 'q' to quit")

# ---------------- UTILITY ----------------
def euclidean_distance(lm1, lm2):
    return math.sqrt((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    pose_results = pose.process(rgb)
    hand_results = hands.process(rgb)

    main_person_bbox = None

    # --- FIND MAIN PERSON (based on shoulders) ---
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # center x,y and approximate size
        cx = (left_shoulder.x + right_shoulder.x) / 2
        cy = (left_shoulder.y + right_shoulder.y) / 2
        size = euclidean_distance(left_shoulder, right_shoulder)

        main_person_bbox = (cx, cy, size)
        mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    interaction_confirmed = False

    # --- CHECK HANDS ONLY NEAR MAIN PERSON ---
    if hand_results.multi_hand_landmarks and main_person_bbox:
        cx, cy, size = main_person_bbox

        for hand_landmarks in hand_results.multi_hand_landmarks:
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

            wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
            middle_mcp_y = int(middle_mcp.y * h)

            # Only consider hand if near main person's shoulders
            if abs(wrist.x - cx) < size and abs(wrist.y - cy) < size:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                if wrist_y < middle_mcp_y:  # hand raised
                    if hand_raised_start is None:
                        hand_raised_start = time.time()
                    elif time.time() - hand_raised_start >= HOLD_TIME:
                        interaction_confirmed = True
                else:
                    hand_raised_start = None
    else:
        hand_raised_start = None

    # --- DISPLAY FEEDBACK ---
    if interaction_confirmed:
        cv2.putText(frame, "INTERACTION STARTED", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    elif hand_raised_start is not None:
        elapsed = time.time() - hand_raised_start
        cv2.putText(frame, f"HOLDING... {elapsed:.1f}s", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    cv2.imshow("Hand Raise Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
