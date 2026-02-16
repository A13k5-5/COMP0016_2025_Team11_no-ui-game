# from gamePlayer import GamePlayer
#
# if __name__ == "__main__":
#     player = GamePlayer()
#     player.playGame("graph.json")

from graph import Node
from storageManager import test_graphs, GameLoader
from storageManager import GameSaver

if __name__ == "__main__":
    graph: Node = test_graphs.test_game()
    saver: GameSaver = GameSaver()
    saver.save_game("C:\\Users\\pison\\Downloads\\no-ui-game\\", "Cool Game", graph)
#
#     loader: GameLoader = GameLoader()
#     loader.load_graph("C:\\Users\\pison\\Downloads\\no-ui-game\\Cool Game")

# if __name__ == "__main__":
#     gesture: Gesture = Gesture(gesture="ILoveYou", handedness="Right")
#     print(gesture.model_dump())

from gamePlayer import GamePlayer
import os

if __name__ == "__main__":
    player = GamePlayer()
    graph: Node = test_graphs.test_game()
    # player._startGameLoop(graph)
    player.playGame(os.path.join(os.path.dirname(__file__), "Cool Game"))
