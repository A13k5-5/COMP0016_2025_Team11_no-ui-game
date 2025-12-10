from graph import Node
from myGestureRecognizer.gestureRecogniserRefactor import GestureRecognizerApp
import time

if __name__ == "__main__":
    # Story nodes with clear choice descriptions that reference handedness
    start = Node(
        "You find yourself at the ruined gate of an old manor. Two paths lie ahead:\n"
        " - Perform the `ILoveYou` gesture with your LEFT hand to slip through the overgrown garden gate.\n"
        " - Perform the `ILoveYou` gesture with your RIGHT hand to take the stone stair into the cellar."
    )
    garden = Node(
        "You slip through the garden, tangled roses parting around you. Moonlight reveals a hidden tool shed."
    )
    cellar = Node(
        "You descend the stone stair into a cold cellar. The air smells of dust and old paper; something moves in the corner."
    )
    shed_find = Node(
        "Inside the shed you find a lantern and rope. This may help later."
    )
    cellar_encounter = Node(
        "A shadow rustles — a friendly stray dog wags its tail, offering companionship."
    )
    loop_back = Node(
        "The path leads back to the gate. You may choose again."
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
