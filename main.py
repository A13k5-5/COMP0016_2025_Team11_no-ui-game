from gamePlayer import GamePlayer
import os

if __name__ == "__main__":
    player = GamePlayer()
    player.playGame(os.path.join(os.path.dirname(__file__), "Cool Game"))
