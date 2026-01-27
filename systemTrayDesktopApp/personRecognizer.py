import os
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"

import cv2
import time
import threading
import mediapipe as mp
import math

from mediapipe.tasks.vision import HandLandmarker, HandLandmarkerOptions, PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks import BaseOptions

# MEDIA PIPE TASKS
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# CONFIG
HOLD_TIME = 2.0  # seconds to hold hand raised
CAMERA_INDEX = 0

# UTILS
def euclidean_distance(lm1, lm2):
    return math.sqrt((lm1.x - lm2.x)**2 + (lm1.y - lm2.y)**2)

# CLASS FOR HAND RAISE DETECTION
class GestureRecognition:
    def __init__(self, hand_model_path="hand_landmarker.task", pose_model_path="pose_landmarker_full.task", target_fps=10):
        self.hand_model_path = hand_model_path
        self.pose_model_path = pose_model_path
        self.target_fps = target_fps
        self.running = False
        self.thread = None
        self.hand_raised_start = None

        # Initialize MediaPipe tasks
        hhand_options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.hand_model_path),
            running_mode=RunningMode.LIVE_STREAM,
            min_hand_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        pose_options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.pose_model_path),
            running_mode=RunningMode.LIVE_STREAM,
            min_pose_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.pose_recognizer = PoseLandmarker.create_from_options(pose_options)

    def _process_frame(self, frame, timestamp_ms):
        h, w, _ = frame.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # --- POSE RECOGNITION ---
        pose_result = self.pose_recognizer.recognize_async(mp_image, timestamp_ms)
        main_person_bbox = None
        if pose_result.pose_landmarks:
            # Take first person detected
            landmarks = pose_result.pose_landmarks[0].landmarks
            left_shoulder = landmarks[11]  # LEFT_SHOULDER
            right_shoulder = landmarks[12] # RIGHT_SHOULDER

            cx = (left_shoulder.x + right_shoulder.x) / 2
            cy = (left_shoulder.y + right_shoulder.y) / 2
            size = euclidean_distance(left_shoulder, right_shoulder)
            main_person_bbox = (cx, cy, size)

        # --- HAND RECOGNITION ---
        hand_result = self.hand_recognizer.recognize_async(mp_image, timestamp_ms)
        interaction_confirmed = False

        if hand_result.hand_landmarks and main_person_bbox:
            cx, cy, size = main_person_bbox
            for hand_landmarks in hand_result.hand_landmarks:
                wrist = hand_landmarks[0]        # WRIST
                middle_mcp = hand_landmarks[9]   # MIDDLE_FINGER_MCP

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

            timestamp = int(time.time() * 1000)
            interaction_confirmed, frame = self._process_frame(frame, timestamp)

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