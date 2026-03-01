import sys
import os

if __name__ == "__main__":

    import gamePlayer

    player = gamePlayer.GamePlayer()
    # player.playGame(os.path.join(os.path.dirname(__file__), "saved_games", "simple game"))
    # player.playGame("./saved_games/simple_game")
    player.playGame(sys.argv[1])

# if __name__ == "__main__":
#     from gui.homePage import run
#     run()
