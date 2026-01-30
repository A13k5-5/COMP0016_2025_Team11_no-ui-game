import logging
import time
import os

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import GestureRecognizer, RunningMode, GestureRecognizerOptions, GestureRecognizerResult

from .videoCaptureManager import video_capture_manager

WINDOW_NAME = "Hand Detection"


class VideoGestureRecogniser:

    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "gesture_recognizer.task")
        self.camera_index = 0
        self._last_gesture: str | None = None
        self._last_handedness: str | None = None

    def _reset(self):
        self._last_gesture = None
        self._last_handedness = None

    def _result_callback(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
        """
        Called by MediaPipe on the listener thread when a result is ready.
        Stores the most confident gesture name for overlaying on the next displayed frame.
        """
        if len(result.gestures) < 1:
            # then no hand detected
            self._last_gesture = None
            return
        # set the last gesture and which hand
        self._last_gesture = result.gestures[0][0].category_name
        self._last_handedness = result.handedness[0][0].category_name

    def _create_recognizer(self):
        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
        )
        return GestureRecognizer.create_from_options(options)

    @staticmethod
    def _send_to_recogniser(frame: mp.Image, recognizer: GestureRecognizer):
        timestamp_ms = int(1000 * time.time())

        # convert and send to recognizer asynchronously
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        recognizer.recognize_async(mp_image, timestamp_ms)

    def run(self, gestures: list[tuple[str, str]]) -> tuple[str, str]:
        with self._create_recognizer() as recognizer, video_capture_manager(self.camera_index) as cap:
            while True:
                ret, frame = cap.read()

                self._send_to_recogniser(frame, recognizer)

                cv2.imshow(WINDOW_NAME, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    logging.info("Quit key pressed")
                    break

