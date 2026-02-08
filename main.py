# from gamePlayer.gamePlayerGUI import GamePlayerGUI
#
# if __name__ == "__main__":
#     player = GamePlayerGUI()
#     player.run()

import cv2 as cv

if __name__ == "__main__":
    cap = cv.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv.imshow("Frame", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
