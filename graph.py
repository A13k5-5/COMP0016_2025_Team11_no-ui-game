from tts import generateAudioFile
import pygame

pygame.init()

class Node:
    def __init__(self, text: str):
        self._text = text
        self.audioFilePath = f"./audioFiles/{text[:10]}.wav"
        # generateAudioFile(text, self.audioFilePath)
        self.adjacencyList: dict[tuple[str, str], str] = {}

    def getText(self):
        # run the audiofile found at self.audioPath
        pygame.mixer.Sound(self.audioFilePath).play()
        return self._text

    def addNode(self, gesture: tuple[str, str], newNode):
        self.adjacencyList[gesture] = newNode

    def getNode(self, gesture: tuple[str, str]):
        return self.adjacencyList[gesture]

    def __str__(self):
        return self._text
