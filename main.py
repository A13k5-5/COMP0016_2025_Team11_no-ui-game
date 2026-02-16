from gamePlayer import GamePlayer
import os

if __name__ == "__main__":
    player = GamePlayer()
    player.playGame(os.path.join(os.path.dirname(__file__), "saved_games", "Lord of the rings"))

# if __name__ == "__main__":
#     from gui.gameCreationPage import run
#     run()
