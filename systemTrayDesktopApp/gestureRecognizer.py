import os
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"

import cv2
import time
import threading
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class GestureRecognition:
    def __init__(self, model_path="gesture_recognizer.task", target_fps=10):
        self.model_path = model_path
        self.target_fps = target_fps
        self.running = False
        self.thread = None
        self.last_gesture = None

    def _on_result(self, result, output_image, timestamp_ms):
        if result.gestures:
            gesture = result.gestures[0][0].category_name
            if gesture != self.last_gesture:
                self.last_gesture = gesture
                print(f"Gesture detected: {gesture}")

    def _run(self):
        cap = cv2.VideoCapture(0)

        #cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        if not cap.isOpened():
            print("Failed to open camera")
            return

        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self._on_result
        )

        frame_interval = 1.0 / self.target_fps

        with GestureRecognizer.create_from_options(options) as recognizer:
            while self.running:
                start_time = time.time()

                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = int(time.time() * 1000)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=frame_rgb
                )

                recognizer.recognize_async(mp_image, timestamp)

                # enforce selected fps
                elapsed = time.time() - start_time
                time.sleep(max(0, frame_interval - elapsed))

        cap.release()
        print("Gesture Recognition stopped")

    def start(self):
        if self.running:
            return
        print("Starting Gesture Recognition")
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        print("Stopping Gesture Recognition")
        self.running = False
