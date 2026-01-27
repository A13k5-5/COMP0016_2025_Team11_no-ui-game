import os
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"

import cv2
import time
import threading
import math
import mediapipe as mp  # <--- public API

# CONFIG
HOLD_TIME = 2.0  # seconds to hold hand raised
CAMERA_INDEX = 0

# UTILS
def euclidean_distance(lm1, lm2):
    return math.sqrt((lm1.x - lm1.x)**2 + (lm1.y - lm2.y)**2)

# CLASS FOR HAND RAISE DETECTION
class GestureRecognition:
    def __init__(self, target_fps=10):
        self.target_fps = target_fps
        self.running = False
        self.thread = None
        self.hand_raised_start = None

        # --- MediaPipe Hands and Pose ---
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

    def _process_frame(self, frame):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # --- POSE ---
        pose_result = self.pose.process(rgb_frame)
        main_person_bbox = None

        if pose_result.pose_landmarks:
            landmarks = pose_result.pose_landmarks.landmark
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]

            cx = (left_shoulder.x + right_shoulder.x) / 2
            cy = (left_shoulder.y + right_shoulder.y) / 2
            size = euclidean_distance(left_shoulder, right_shoulder)
            main_person_bbox = (cx, cy, size)

        # --- HANDS ---
        hand_result = self.hands.process(rgb_frame)
        interaction_confirmed = False

        if hand_result.multi_hand_landmarks and main_person_bbox:
            cx, cy, size = main_person_bbox
            for hand_landmarks in hand_result.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                middle_mcp = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                if abs(wrist.x - cx) < size and abs(wrist.y - cy) < size:
                    wrist_y = int(wrist.y * h)
                    middle_mcp_y = int(middle_mcp.y * h)

                    if wrist_y < middle_mcp_y:  # hand raised
                        if self.hand_raised_start is None:
                            self.hand_raised_start = time.time()
                        elif time.time() - self.hand_raised_start >= HOLD_TIME:
                            interaction_confirmed = True
                    else:
                        self.hand_raised_start = None
        else:
            self.hand_raised_start = None

        return interaction_confirmed, frame

    def _run(self):
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            print("Failed to open camera")
            return

        frame_interval = 1.0 / self.target_fps

        while self.running:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                break

            interaction_confirmed, frame = self._process_frame(frame)

            # Display feedback
            if interaction_confirmed:
                cv2.putText(frame, "INTERACTION STARTED", (40, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            elif self.hand_raised_start is not None:
                elapsed = time.time() - self.hand_raised_start
                cv2.putText(frame, f"HOLDING... {elapsed:.1f}s", (40, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

            cv2.imshow("Hand Raise Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            elapsed = time.time() - start_time
            time.sleep(max(0, frame_interval - elapsed))

        cap.release()
        cv2.destroyAllWindows()

    def start(self):
        if self.running:
            return
        print("Starting Hand Raise Detector")
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        print("Stopping Hand Raise Detector")
        self.running = False
