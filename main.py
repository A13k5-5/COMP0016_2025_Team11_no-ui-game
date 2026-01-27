from graph import Node
from myGestureRecognizer.gestureRecogniserRefactor import GestureRecognizerApp
import time

if __name__ == "__main__":
    # Story nodes with clear choice descriptions that reference handedness
    start = Node(
        "You find yourself at the ruined gate of an old manor. Two paths lie ahead:"
        "Options:"
        " - Left: Go through the garden (leads to the shed)."
        " - Right: Go down the cellar stairs (leads to the cellar)."
    )
    garden = Node(
        "You slip through the garden, tangled roses parting around you. Moonlight reveals a hidden tool shed."
        "Options:"
        " - Left: Enter the shed and search (leads to finding a lantern and rope)."
        " - Right: Follow a winding path that leads back toward the gate."
    )
    cellar = Node(
        "You descend the stone stair into a cold cellar. The air smells of dust and old paper; something moves in the corner."
        "Options:"
        " - Left: Retreat and head back toward the gate."
        " - Right: Approach the corner (may reveal an encounter)."
    )
    shed_find = Node(
        "Inside the shed you find a lantern and rope. This may help later."
        "Options:"
        " - Left: Leave the shed and return toward the gate."
        " - Right: Take a different path that leads toward the cellar encounter."
    )
    cellar_encounter = Node(
        "A shadow rustles — a friendly stray dog wags its tail, offering companionship."
        "Options:"
        " - Left: Escort the dog back toward the gate."
        " - Right: Continue on a path that also leads back toward the gate."
    )
    loop_back = Node(
        "The path leads back to the gate. You may choose again."
        "Options:"
        " - Left: Reattempt the gate choices (Left -> garden)."
        " - Right: Reattempt the gate choices (Right -> cellar)."
    )

    # All connections use the same gesture key `ILoveYou`; handedness decides the branch
    start.addNode(("ILoveYou", "Left"), garden)
    start.addNode(("ILoveYou", "Right"), cellar)

    garden.addNode(("ILoveYou", "Left"), shed_find)
    garden.addNode(("ILoveYou", "Right"), loop_back)

    cellar.addNode(("ILoveYou", "Left"), loop_back)
    cellar.addNode(("ILoveYou", "Right"), cellar_encounter)

    shed_find.addNode(("ILoveYou", "Left"), loop_back)
    shed_find.addNode(("ILoveYou", "Right"), cellar_encounter)

    cellar_encounter.addNode(("ILoveYou", "Left"), loop_back)
    cellar_encounter.addNode(("ILoveYou", "Right"), loop_back)

    loop_back.addNode(("ILoveYou", "Left"), start)
    loop_back.addNode(("ILoveYou", "Right"), start)

    curNode: Node = start

    LOW_FPS_MODE = True
    if LOW_FPS_MODE:
        recogniser: GestureRecognizerApp = GestureRecognizerApp(frame_rate=5.0)
    else:
        recogniser: GestureRecognizerApp = GestureRecognizerApp()

    while True:
        # Display current scene and available choices (explicit about handedness)
        print("\n" + curNode.getText() + "\n")
        # Build readable option list for console preview
        options = list(curNode.adjacencyList.items())
        print("Choices (perform `ILoveYou` gesture with the shown hand):")
        for idx, (key, node) in enumerate(options, start=1):
            gesture, handedness = key
            # show a short preview of the destination and the required handedness
            print(f" {idx}. Hand: {handedness} -> {node._text.split('.')[0]}")

        # Ask recogniser for a decision (expects a tuple like ("ILoveYou", "Left"))
        decision = recogniser.run(list(curNode.adjacencyList.keys()))

        if not decision:
            print("Unrecognised input from recogniser. Please try again.")
            continue

        next_node = curNode.getNode(decision)
        if not next_node:
            print("That gesture/hand combination is not valid here. Try again.")
            continue

        curNode = next_node
        time.sleep(3)
