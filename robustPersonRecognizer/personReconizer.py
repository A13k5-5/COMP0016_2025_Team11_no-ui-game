import cv2
import time
import threading
import numpy as np
from openvino.runtime import Core
import mediapipe as mp

CAMERA_INDEX = 0
HOLD_TIME = 2.0  # seconds to confirm interaction
TARGET_FPS = 10
PERSON_MODEL_PATH = "person-detection-0200.xml"
GESTURE_MODEL_PATH = "gesture_recognizer.task"
CONFIDENCE_THRESHOLD = 0.6

ie = Core()
person_model = ie.read_model(model=PERSON_MODEL_PATH)
compiled_model = ie.compile_model(person_model, "CPU")
input_layer = compiled_model.input(0)
output_layer = compiled_model.output(0)

def detect_main_person(frame):
    """
    Detect people in the frame using OpenVINO person-detection-0200
    Returns the bounding box of the largest person (top, left, bottom, right)
    """
    h, w, _ = frame.shape
    resized = cv2.resize(frame, (256, 256))  # model input size
    input_image = np.expand_dims(resized.transpose(2, 0, 1), 0).astype(np.float32)

    results = compiled_model([input_image])[output_layer]
    boxes = []

    # Convert model output to bounding boxes
    for obj in results[0][0]:
        label, conf, xmin, ymin, xmax, ymax = obj
        if conf > CONFIDENCE_THRESHOLD:
            boxes.append((
                int(ymin * h), int(xmin * w), int(ymax * h), int(xmax * w),
                conf
            ))

    if not boxes:
        return None

    # Return largest box (main person)
    main_box = max(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
    return main_box[:4]

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class HandRaiseDetector:
    def __init__(self, model_path=GESTURE_MODEL_PATH, target_fps=TARGET_FPS):
        self.model_path = model_path
        self.target_fps = target_fps
        self.running = False
        self.thread = None
        self.last_gesture = None
        self.hand_raised_start = None

    def _on_result(self, result, output_image, timestamp_ms):
        if result.gestures:
            gesture = result.gestures[0][0].category_name
            score = result.gestures[0][0].score
            if score > 0.7 and gesture != self.last_gesture:
                self.last_gesture = gesture
                print(f"Gesture detected: {gesture} ({score:.2f})")

                # Simple logic: if gesture is "hand raise", start hold timer
                if gesture.lower() == "hand raise":
                    if self.hand_raised_start is None:
                        self.hand_raised_start = time.time()
                else:
                    self.hand_raised_start = None
        else:
            self.hand_raised_start = None

    def _run(self):
        cap = cv2.VideoCapture(CAMERA_INDEX)
        frame_interval = 1.0 / self.target_fps

        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self._on_result
        )

        with GestureRecognizer.create_from_options(options) as recognizer:
            while self.running:
                start_time = time.time()
                ret, frame = cap.read()
                if not ret:
                    continue

                main_box = detect_main_person(frame)
                if main_box:
                    top, left, bottom, right = main_box
                    cropped = frame[top:bottom, left:right]
                    frame_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB,
                        data=frame_rgb
                    )
                    timestamp = int(time.time() * 1000)
                    recognizer.recognize_async(mp_image, timestamp)

                    # Visualize main person
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Show hold status
                interaction_confirmed = False
                if self.hand_raised_start:
                    elapsed = time.time() - self.hand_raised_start
                    if elapsed >= HOLD_TIME:
                        interaction_confirmed = True
                        cv2.putText(frame, "INTERACTION STARTED",
                                    (40, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                    1.2, (0, 255, 0), 3)
                    else:
                        cv2.putText(frame, f"HOLDING... {elapsed:.1f}s",
                                    (40, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                    1.0, (0, 255, 255), 2)

                cv2.imshow("Hand Raise Detector", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break

                # enforce FPS
                elapsed = time.time() - start_time
                time.sleep(max(0, frame_interval - elapsed))

        cap.release()
        cv2.destroyAllWindows()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

if __name__ == "__main__":
    print()
    detector = HandRaiseDetector()
    detector.start()
    detector.thread.join()