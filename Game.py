__author__ = 'Simon'
"""Python CargoLander is a game, in which you control packet delivery drones

This game is inspired by the classical moonlander and reassesses the topic with current "drone packet delivery" technology.
The goal is to safely land color-coded drones on the corresponding platform/doormat.
"""

import Lander
import Platform
import Assets
import Highscore
import enums
import pygame
from pygame.locals import *


class Game(object):
    """Create Game object to host main loop and highscores"""

    def __init__(self, x, y):
        self.landerList = list()
        self.landerCount = 0
        self.platformList = list()
        self.score = 0
        self.lives = 4
        self.crashed = 0
        self.GAMESTATE = enums.GAMESTATE.STARTSCREEN
        self.drawSize = (x, y)
        pygame.init()
        self.screen = pygame.display.set_mode(self.drawSize)
        self.landingLog = list()
        self.secondsLeft = 75
        self.topBar = None
        self.assets = Assets.Assets()
        self.playerName = ""
        self.highscore = Highscore.Highscore("highscores.xml")
        self.scored = False

    def run(self):
        """Initialise and run game loop"""
        clock = pygame.time.Clock()
        pygame.display.set_caption('Cargo Lander v0.9')
        pygame.mouse.set_visible(True)
        cursor = self.cursor_crosshair()
        pygame.mouse.set_cursor((24, 24), (12, 12), *cursor)
        self.initPlatforms()
        self.drawTopBar()
        gameArea = pygame.Surface((self.drawSize[0], self.drawSize[1] - 20))
        while True:
            deltaTime = clock.tick(60) / 1000.0
            self.processInput()
            if self.GAMESTATE == enums.GAMESTATE.QUIT:
                return
            gameArea.blit(self.assets.background, (0, 0))
            self.drawPlatforms(gameArea)
            self.updateTimeLeft(deltaTime)
            self.drawTopBar()
            if self.GAMESTATE == enums.GAMESTATE.RUNNING:
                self.updateLanders(gameArea, deltaTime)
            if self.GAMESTATE == enums.GAMESTATE.GAMEOVER:
                self.gameOverScreen(gameArea, "GAME OVER")
            if self.GAMESTATE == enums.GAMESTATE.TIMEUP:
                self.gameOverScreen(gameArea, "TIME IS UP")
            if self.GAMESTATE == enums.GAMESTATE.STARTSCREEN:
                self.startScreen(gameArea)
            if self.GAMESTATE == enums.GAMESTATE.HELPSCREEN:
                self.helpScreen(gameArea)
            self.screen.blit(gameArea, (0, 20))
            self.screen.blit(self.topBar, (0, 0))
            pygame.display.flip()
            self.checkGameOver()


    def updateLanders(self, screen, deltaTime):
        """Analyse list of lander objects

         Loop through all landers known to the game and do:
            * call x.update() on landers if x.isAlive
            * calculate score on landers if x.hasScored
        """
        newScore = 0
        newCount = 0
        noCrashed = 0
        self.spawnLander()
        for lander in self.landerList:
            if lander.isAlive:
                newCount += 1
                lander.update(deltaTime, screen, self.assets, self.landingLog)
            elif lander.hasScored:
                if lander.color == lander.collisionPartner.color:
                    newScore += 3
                else:
                    newScore += 1
            elif lander.hasCrashed:
                noCrashed += 1
        self.score = newScore
        self.crashed = noCrashed
        self.landerCount = newCount

    def drawPlatforms(self, surface):
        """Draw static landing platforms"""
        for platform in self.platformList:
            platform.drawPlatform(surface)

    def processInput(self):
        """Handle event input (key and mouse)

        Space spawns a new lander per press.
        Escape quits the game
        Keydown events trigger thrust for either up or left/right
        Keyup events trigger unthrust for either up or left/right
        Click events call lander.clicked to check collision and trigger thrust on a single lander while clicked
        """
        for event in pygame.event.get():
            if self.GAMESTATE not in (enums.GAMESTATE.STARTSCREEN, enums.GAMESTATE.HELPSCREEN):
                if event.type == pygame.QUIT:
                    self.GAMESTATE = enums.GAMESTATE.QUIT
                # KEYDOWN and KEYUP are handled separately to allow press and hold actions
                if event.type == pygame.KEYDOWN:
                    if event.key == K_f:
                        pygame.display.toggle_fullscreen()
                    if event.key == K_ESCAPE:
                        self.GAMESTATE = enums.GAMESTATE.QUIT
                    if event.key == K_r and (self.GAMESTATE == enums.GAMESTATE.GAMEOVER or self.GAMESTATE == enums.GAMESTATE.TIMEUP):
                        self.restart()
                    if event.key == K_UP:
                        for l in self.landerList:
                            l.thrust()
                    if event.key == K_SPACE:
                        self.spawnLander(forced=True)
                    if event.key == K_LEFT:
                        for l in self.landerList:
                            l.horizontalThrust("LEFT")
                    if event.key == K_RIGHT:
                        for l in self.landerList:
                            l.horizontalThrust("RIGHT")
                # KEYDOWN and KEYUP are handled seperately to allow press and hold actions
                if event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        for l in self.landerList:
                            l.unthrust()
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        for l in self.landerList:
                            l.horizontalUnthrust()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for l in self.landerList:
                        l.clicked(event.pos)
                if event.type == pygame.MOUSEBUTTONUP:
                    for l in self.landerList:
                        l.unthrust()
            else:
                pygame.key.set_repeat(500, 30)
                pygame.key.set_mods(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == K_RETURN:
                        self.GAMESTATE = enums.GAMESTATE.RUNNING
                    elif event.key == K_ESCAPE:
                        self.GAMESTATE = enums.GAMESTATE.QUIT
                    elif event.key == K_BACKSPACE:
                        self.playerName = self.playerName[:-1]
                    elif event.key in range(97, 123):
                        self.playerName += chr(event.key)
                    elif event.key == K_TAB:
                        self.setHelp(True)
                if event.type == pygame.KEYUP:
                    if event.key == K_TAB:
                        self.setHelp(False)
                self.playerName = self.playerName.upper()


    def spawnLander(self, forced=False):
        """Create and add a Lander object to landerList

            * Whenever there is no lander left on screen
            * Or when there is forced spawning (e.g. space bar hit)
        """
        if self.landerCount == 0 or forced:
            myLander = Lander.Lander(self, self.landerList, self.platformList)
            self.landerList.append(myLander)

    def initPlatforms(self):
        """Create and add platforms to platformList"""
        myPlatform = Platform.Platform((255, 0, 0), 10)
        self.platformList.append(myPlatform)
        myPlatform = Platform.Platform((255, 255, 0), 115)
        self.platformList.append(myPlatform)
        myPlatform = Platform.Platform((0, 0, 255), 220)
        self.platformList.append(myPlatform)

    def cursor_crosshair(self):
        """Return compiled ASCII art mouse cursor"""
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

    def showScore(self, screen):
        """Display current score in upper-right corner.

        'No one will ever need more than 3-digits for a scoreboard' - Simon Schliesky March 5th 2014"""
        # Create a font
        font = pygame.font.Font(None, 17)
        text = font.render('%03d' % self.score, True, (255,
        255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.x = self.drawSize[0] - textRect.width - 10
        textRect.y = 2
        screen.blit(text, textRect)

    def showTime(self, screen):
        """Display current time in the center of topbar."""
        # Create a font
        font = pygame.font.Font(None, 17)
        text = font.render('%02d' % self.secondsLeft, True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()
        textRect.centerx = (self.drawSize[0] - textRect.width) / 2
        textRect.y = 2
        screen.blit(text, textRect)

    def showLives(self, screen):
        for x in range(0, self.lives - self.crashed):
            icon = pygame.Surface((5, 5))
            icon.fill((255, 0, 0))
            screen.blit(icon, (5 + 10*x, 2))

    def checkGameOver(self):
        if self.lives <= self.crashed and self.GAMESTATE != enums.GAMESTATE.QUIT:
            self.GAMESTATE = enums.GAMESTATE.GAMEOVER

    def gameOverScreen(self, screen, text):
        shade = pygame.Surface(screen.get_size())
        shade.fill((50, 50, 50))
        shade.set_alpha(64)
        # GAMEOVER
        font = pygame.font.Font(None, 32)
        text = font.render(text, True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 - 50
        screen.blit(shade, (0, 0))
        screen.blit(text, textRect)
        self.highscore.drawHighscore(screen)
        # Score
        if not self.scored and self.score > 0:
            self.highscore.insertScore(name=self.playerName, score=self.score)
            self.highscore.writeHighscores()
            self.scored = True
        font = pygame.font.Font(None, 20)
        text = font.render('%03d' % self.score, True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 + 50
        screen.blit(text, textRect)
        text = font.render('Press R for new round', True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = 25
        screen.blit(text, textRect)

    def restart(self):
        self.landerList = list()
        self.landerCount = 0
        self.platformList = list()
        self.score = 0
        self.lives = 4
        self.crashed = 0
        self.secondsLeft = 90
        self.GAMESTATE = enums.GAMESTATE.STARTSCREEN
        self.initPlatforms()

    def drawTopBar(self):
        topBar = pygame.Surface((self.drawSize[0], 20))
        topBar.fill((0, 0, 0))
        self.showScore(topBar)
        self.showLives(topBar)
        self.showTime(topBar)
        self.topBar = topBar

    def updateTimeLeft(self, deltatime):
        if self.GAMESTATE == enums.GAMESTATE.RUNNING:
            if self.secondsLeft <= 0:
                self.GAMESTATE = enums.GAMESTATE.TIMEUP
            else:
                self.secondsLeft -= deltatime

    def startScreen(self, screen):
        """Draw start screen and ask for name
        """
        shade = pygame.Surface(screen.get_size())
        shade.fill((0, 0, 0))
        shade.set_alpha(200)
        screen.blit(shade, (0, 0))
        font = pygame.font.Font(None, 20)
        text = font.render(self.playerName, True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 + 35
        screen.blit(text, textRect)

        text = font.render("Input name", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 + 50
        screen.blit(text, textRect)
        text = font.render("Press Enter", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 + 80
        screen.blit(text, textRect)
        text = font.render("to start game", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 + 96
        screen.blit(text, textRect)

        text = font.render("Press and hold tab", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 - 80
        screen.blit(text, textRect)
        text = font.render("for help", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.centerx = self.drawSize[0]/2
        textRect.centery = self.drawSize[1]/2 - 62
        screen.blit(text, textRect)

    def helpScreen(self, screen):
        """Draw help screen and ask for name
        """
        shade = pygame.Surface(screen.get_size())
        shade.fill((0, 0, 0))
        shade.set_alpha(200)
        screen.blit(shade, (0, 0))
        font = pygame.font.Font(None, 20)

        screen.blit(self.assets.upArrow, (5, 20))
        text = font.render("Accelerate drones upwards", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.x = 60
        textRect.centery = 30
        screen.blit(text, textRect)

        screen.blit(self.assets.leftArrow, (5, 50))
        screen.blit(self.assets.rightArrow, (30, 50))
        text = font.render("Steer left/right", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.x = 60
        textRect.centery = 60
        screen.blit(text, textRect)

        screen.blit(self.assets.space, (5, 80))
        text = font.render("Spawn another drone", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.x = 60
        textRect.centery = 90
        screen.blit(text, textRect)

        screen.blit(self.assets.ESC, (5, 110))
        text = font.render("Quit game", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.x = 60
        textRect.centery = 120
        screen.blit(text, textRect)

        screen.blit(self.assets.mouse, (5, 140))
        text = font.render("Accelerate single drone", True, (255, 255, 255, 0))
        textRect = text.get_rect()
        textRect.x = 60
        textRect.centery = 150
        screen.blit(text, textRect)

    def setHelp(self, activate):
        if activate:
            self.GAMESTATE = enums.GAMESTATE.HELPSCREEN
        else:
            self.GAMESTATE = enums.GAMESTATE.STARTSCREEN


if __name__ == "__main__":
    xdim = 320
    ydim = 480
    myGame = Game(xdim, ydim)
    myGame.run()