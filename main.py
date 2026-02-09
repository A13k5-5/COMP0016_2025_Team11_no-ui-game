# from gamePlayer import GamePlayer
#
# if __name__ == "__main__":
#     player = GamePlayer()
#     player.playGame("graph.json")

from graph import Node
from storageManager import test_graphs
from storageManager import GameSaver

if __name__ == "__main__":
    graph: Node = test_graphs.test_game()
    saver = GameSaver()
    saver.save_game("C:\\Users\\pison\\Downloads\\no-ui-game\\", "Cool Game", graph)
