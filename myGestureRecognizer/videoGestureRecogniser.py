import time
import os

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, RunningMode, GestureRecognizerOptions, \
    GestureRecognizerResult

from gesture import Gesture
from .videoCaptureManager import video_capture_manager

WINDOW_NAME = "Hand Detection"
TIMEOUT_TIME = 30.0 # seconds


class VideoGestureRecogniser:
    """
    Class to handle gesture recognition using MediaPipe's GestureRecognizer.
    """

    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "gesture_recognizer.task")
        self.camera_index = 0
        self._running: bool = True
        self._last_gesture_category: str | None = None
        self._last_handedness: str | None = None
        self._gestures_to_spot: list[Gesture] = []

    def _get_last_gesture(self) -> Gesture:
        return Gesture(gesture=self._last_gesture_category, handedness=self._last_handedness)

    def _reset(self, gestures_to_spot: list[Gesture]):
        self._running = True
        self._last_gesture_category = None
        self._last_handedness = None
        self._gestures_to_spot = gestures_to_spot

    def _stop(self):
        self._running = False

    def _create_recognizer(self):
        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
        )
        return GestureRecognizer.create_from_options(options)

    def _send_to_recognizer(self, frame: mp.Image, recognizer: GestureRecognizer):
        """
        Convert and send to recognizer asynchronously.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(1000 * time.time())
        recognizer.recognize_async(mp_image, timestamp_ms)

    def _result_callback(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        """
        Run for each picture analysed by the recognizer. If a gesture to spot is detected, stop the recognition.
        """
        if len(result.gestures) < 1:
            # then no hand detected
            return
        # set the last gesture
        self._last_gesture_category = result.gestures[0][0].category_name
        self._last_handedness = result.handedness[0][0].category_name
        if self._get_last_gesture() in self._gestures_to_spot:
            self._stop()

    def timeout_stop(self, start_time: float, timeout_duration: float):
        """
        Stop the recognition due to timeout.
        """
        if time.time() - start_time > timeout_duration:
            raise TimeoutError(f"Gesture recognition timed out after {timeout_duration} seconds.")

    def _start_recognition(self):
        """
        Start the video capture and gesture recognition loop. This loop stops when a gesture to spot is detected. The
        code for this can be found in the _result_callback method.
        Raises TimeoutError if no gesture is detected within 30 seconds.
        """
        start = time.time()
        with self._create_recognizer() as recognizer, video_capture_manager(self.camera_index) as cap:
            while self._running:

                ret, frame = cap.read()
                self.timeout_stop(start, TIMEOUT_TIME)

                if not ret:
                    print("Failed to grab frame from camera.")
                    continue

                self._send_to_recognizer(frame, recognizer)

                cv2.imshow(WINDOW_NAME, frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    def get_gesture(self, gestures_to_spot: list[Gesture]) -> Gesture:
        """
        Start the gesture recognition process and return the first gesture detected that is in the gestures_to_spot list.
        :param gestures_to_spot:
        :return:
        """
        self._reset(gestures_to_spot)
        self._start_recognition()
        return self._get_last_gesture()
