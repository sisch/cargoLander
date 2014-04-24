__author__ = 'Simon'
import pygame

class Platform(object):
    def __init__(self, color, xPos):
        self.color = color
        #alt. random color ((255, 0, 0), (0, 0, 255), (255, 255, 0))[random.randint(0, 2)]
        self.xPos = xPos
        self.yPos = 427
        self.drawSize = (90, 5)
        self.type = "PLATFORM"
        self.isAlive = True  # isAlive is added(never used) for compatibility with checkCollision of Lander class

    def drawPlatform(self, surface):
        pygame.draw.rect(surface, self.color, ((self.xPos, self.yPos), self.drawSize), 0)

