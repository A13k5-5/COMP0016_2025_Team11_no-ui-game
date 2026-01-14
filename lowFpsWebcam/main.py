import threading
import time
import cv2

class CameraWorker(threading.Thread):
    def __init__(self, target_fps=10):
        super().__init__()
        self.running = False
        self.target_fps = target_fps

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Camera failed to open")
            return

        print("Camera started")

        frame_count = 0
        last_fps_time = time.time()
        frame_interval = 1.0 / self.target_fps

        while self.running:
            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

            frame_count += 1
            now = time.time()
            if now - last_fps_time >= 1.0:
                fps = frame_count / (now - last_fps_time)
                print(f"FPS: {fps:.2f}")
                frame_count = 0
                last_fps_time = now

            # cap.set(cv2.CAP_PROP_FPS, 10)
            elapsed = time.time() - start_time
            time.sleep(max(0, int(frame_interval - elapsed)))

        cap.release()
        cv2.destroyAllWindows()
        print("Camera stopped")

    def stop(self):
        self.running = False

camera_worker = CameraWorker(target_fps=10)
camera_worker.start()
