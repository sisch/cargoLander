__author__ = 'Simon'
"""Python CargoLander is a game, in which you control packet delivery drones

This game is inspired by the classical moonlander and reassesses the topic with current "drone packet delivery" technology.
The goal is to safely land color-coded drones on the corresponding platform/doormat.
"""

import Lander
import Platform
import pygame
from pygame.locals import *
import time

startTime = time.time()
SCOREINTERVAL = 5
class Game(object):
    """class: Game

    contains the main game loop and highscores
    """

    def __init__(self, x, y):
        self.landerList = list()
        self.landerCount = 0
        self.platformList = list()
        self.drawSize = (x, y)
        pygame.init()
        self.screen = pygame.display.set_mode(self.drawSize)
        self.score = 0
        self.landingLog = list()
        self.seconds = 0

    def run(self):
        global startTime
        self.RUNNING = True
        clock = pygame.time.Clock()
        pygame.display.set_caption('Basic Pygame program')
        pygame.mouse.set_visible(True)
        self.initPlatforms()
        cursor = self.cursor_crosshair()
        pygame.mouse.set_cursor((24, 24), (12, 12), *cursor)
        background = pygame.Surface(self.screen.get_size())
        while self.RUNNING:
            deltaTime = clock.tick(60) / 1000.0
            self.processInput()
            background.fill((50, 50, 150))
            self.updateLanders(background, deltaTime)
            self.showScore(deltaTime, background)
            self.drawPlatforms(background)
            self.screen.blit(background, (0, 0))
            pygame.display.flip()

    def updateLanders(self, screen, deltaTime):
        """def: updateLanders

        Curates list of landers (removing deleted ones) and calls position update functions.
        """
        newScore = 0
        for lander in self.landerList:
            if lander.isAlive:
                lander.update(deltaTime, screen, self.landingLog, self.landerList + self.platformList)
            if lander.hasScored:
                if lander.color == lander.collisionPartner.color:
                    newScore += 3
                else:
                    newScore += 1
        self.score = newScore

    def drawPlatforms(self, surface):
        for platform in self.platformList:
            platform.drawPlatform(surface)

    def processInput(self):
        """processInput handles key and mouse actions

        Keydown and keyup events are distinguished for keyboard as well as mouse input.
        Space spawns a new lander per click.
        Clicking on a lander calls the clicked routine to check collision and thrusts the lander that is clicked

        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 self.RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.RUNNING = False
                if event.key == K_UP:
                    for l in self.landerList:
                        l.thrust()
                if event.key == K_SPACE:
                    self.spawnLander()
                if event.key == K_LEFT:
                    for l in self.landerList:
                        l.horizontalThrust("LEFT")
                if event.key == K_RIGHT:
                    for l in self.landerList:
                        l.horizontalThrust("RIGHT")

            if event.type == pygame.KEYUP:
                if event.key == K_UP:
                    for l in self.landerList:
                        l.unthrust()
                if event.key == K_LEFT or event.key == K_RIGHT:
                    for l in self.landerList:
                        l.horizontalUnthrust()

            #keys = pygame.key.get_pressed()
            #if keys[pygame.K_RIGHT]:
            #    for l in self.landerList:
            #        l.horizontalSpeed += 5
            #if keys[pygame.K_LEFT]:
            #    for l in self.landerList:
            #        l.horizontalSpeed -= 5

            if event.type == pygame.MOUSEBUTTONDOWN:
                for l in self.landerList:
                    l.clicked(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                for l in self.landerList:
                    l.unthrust()

    def spawnLander(self):
        myLander = Lander.Lander()
        self.landerList.append(myLander)
        self.landerCount += 1

    def initPlatforms(self):
        myPlatform = Platform.Platform((255, 0, 0), 10)
        self.platformList.append(myPlatform)
        myPlatform = Platform.Platform((255, 255, 0), 115)
        self.platformList.append(myPlatform)
        myPlatform = Platform.Platform((0, 0, 255), 220)
        self.platformList.append(myPlatform)


    def cursor_crosshair(self):
        strings = (
            "          XXXX          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "XXXXXXXXXXX..XXXXXXXXXXX",
            "X..........XX..........X",
            "X..........XX..........X",
            "XXXXXXXXXXX..XXXXXXXXXXX",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          X..X          ",
            "          XXXX          "
        )
        return pygame.cursors.compile(strings, black='.',white='X',xor='o')

    def showScore(self, deltaTime, screen):
        # Create a font
        font = pygame.font.Font(None, 17)
        text = font.render('%03d' % self.score, True, (255,
        255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.x = self.drawSize[0] - textRect.width - 10
        textRect.y = 10
        screen.blit(text, textRect)


if __name__ == "__main__":
    myGame = Game(320, 480)
    myGame.run()