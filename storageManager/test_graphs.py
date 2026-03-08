from gesture import EnumGesture
from graph import Node


def build_default_story_graph() -> Node:
    # --- The Fellowship at the Mines of Moria ---

    start = Node(
        "You are Frodo before the Doors of Durin. Gandalf studies the inscription: 'Speak, friend, and enter.'",
        left_option="Help Gandalf solve the riddle",
        right_option="Warn the Fellowship about the lake"
    )

    riddle = Node(
        "Gandalf speaks 'Mellon' and the doors swing open. But a tentacle seizes Frodo!",
        left_option="Slash the tentacle with a knife",
        right_option="Call for Aragorn's help"
    )

    freed = Node(
        "You break free and the Fellowship rushes inside before the doors slam shut. The only way is forward.",
        left_option="Follow Gandalf deeper into the mines",
        right_option="Draw Sting and stay on guard"
    )

    chamber_of_mazarbul = Node(
        "You reach the Chamber of Mazarbul. Suddenly orcs pour in and a cave troll bursts through the wall!",
        left_option="Stab the cave troll in the foot",
        right_option="Hide behind the stone tomb"
    )

    balrog_bridge = Node(
        "The Fellowship flees to the Bridge of Khazad-dûm. A Balrog of Morgoth fills the hall with shadow and flame.",
        left_option="Run across the bridge",
        right_option="Stay close to Gandalf"
    )

    gandalf_falls = Node(
        "Gandalf cries 'You shall not pass!' and falls into the darkness. 'Fly, you fools!'",
        left_option="Flee as Aragorn commands",
        right_option="Reach out toward the dark"
    )

    survived = Node(
        "The Fellowship bursts into sunlight on the slopes of Caradhras. You have escaped Moria.",
        left_option="",
        right_option=""
    )
    survived.is_win = True

    # Connections
    start.addNode(EnumGesture.ILoveYou_Left, riddle)
    start.addNode(EnumGesture.ILoveYou_Right, freed)

    riddle.addNode(EnumGesture.ILoveYou_Left, freed)
    riddle.addNode(EnumGesture.ILoveYou_Right, freed)

    freed.addNode(EnumGesture.ILoveYou_Left, chamber_of_mazarbul)
    freed.addNode(EnumGesture.ILoveYou_Right, chamber_of_mazarbul)

    chamber_of_mazarbul.addNode(EnumGesture.ILoveYou_Left, balrog_bridge)
    chamber_of_mazarbul.addNode(EnumGesture.ILoveYou_Right, balrog_bridge)

    balrog_bridge.addNode(EnumGesture.ILoveYou_Left, gandalf_falls)
    balrog_bridge.addNode(EnumGesture.ILoveYou_Right, gandalf_falls)

    gandalf_falls.addNode(EnumGesture.ILoveYou_Left, survived)
    gandalf_falls.addNode(EnumGesture.ILoveYou_Right, survived)

    return start


def test_game() -> Node:
    root: Node = Node("Hi Bilbo. May I come in?")
    nodeA: Node = Node("Sure come on in.")
    nodeB: Node = Node("No, I'm busy right now. Come tomorrow.")
    root.addNode(EnumGesture.ILoveYou_Left, nodeA)
    root.addNode(EnumGesture.ILoveYou_Right, nodeB)

    return root
