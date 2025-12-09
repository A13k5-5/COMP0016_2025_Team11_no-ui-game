import mediapipe as mp
import cv2
import time


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open webcam")
    exit()

prev_time = 0.0

with mp_hands.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
        
        # compute FPS
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time) if prev_time != 0 else 0.0
        prev_time = curr_time

        # prepare overlay text
        hand_count = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
        title_text = "Hand gesture recognition"
        info_text = f"Hands: {hand_count}  FPS: {fps:.1f}"

        # put texts on the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, title_text, (10, 30), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, info_text, (10, 60), font, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

        # show the frame
        cv2.imshow('Hand Detection', frame)

        print('Sign Language Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break