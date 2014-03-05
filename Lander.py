__author__ = 'Simon'

import random
import pygame
from pygame.locals import *

GRAVITY = 15  # 9.98 # Earth value
CRASHSPEED = 40.0


class Lander(object):
    def __init__(self):
        self.fallSpeed = 0
        self.thrustPower = 25.0
        self.yPos = 0
        self.color = ((255, 0, 0), (0, 0, 255), (255, 255, 0))[random.randint(0, 2)]
        self._isThrustOn = False
        self.xPos = random.randrange(10, 280)
        self.horizontalSpeed = 0.0
        self.drawSize = (40, 40)
        self.isAlive = True
        self.type = "LANDER"
        self.hasScored = False
        self.collisionPartner = None
        self.boundingBox = {"x1": 0, "x2": 0, "y1": 0, "y2": 0}
        self._horizontalThrustLeftOn = False
        self._horizontalThrustRightOn = False

    def thrust(self):
        self._isThrustOn = True

    def unthrust(self):
        self._isThrustOn = False

    def horizontalThrust(self, direction):
        self._horizontalThrustLeftOn = direction == "LEFT"
        self._horizontalThrustRightOn = direction == "RIGHT"

    def horizontalUnthrust(self):
        self._horizontalThrustLeftOn = False
        self._horizontalThrustRightOn = False

    def updateFallspeed(self, deltaTime):
        global GRAVITY
        self.fallSpeed += ((GRAVITY - (self.thrustPower * self._isThrustOn)) * deltaTime)
        if self.yPos <= 0.5:
            self.fallSpeed = max(0, self.fallSpeed)
        self.horizontalSpeed += ((self.thrustPower * -self._horizontalThrustLeftOn) + (self.thrustPower * self._horizontalThrustRightOn)) * deltaTime
        self.horizontalSpeed -= (0.5 * self.horizontalSpeed) * deltaTime

    def updateCoordinates(self, deltaTime):
        self.xPos += (self.horizontalSpeed * deltaTime)
        self.xPos %= 310
        self.yPos = max(self.yPos + (self.fallSpeed * deltaTime), 0)


    def checkCollision(self, object):
        if object == self or not object.isAlive:
            return "CLEAR"
        if self.yPos > 460: # replace with screen size height
            self.collisionPartner = "EDGE"
            return "CRASHED"
        # in Java
        # if(!(box1.x > box2.x + box2.width
        # ||  box1.x + box1.width < box2.x
        # ||  box1.y > box2.y + box2.height
        # ||  box1.y + box1.height < box2.y))
        if not((object.yPos + object.drawSize[1]) < self.boundingBox["y1"]
                or object.yPos > self.boundingBox["y2"]):
            if not((object.xPos + object.drawSize[0]) < self.boundingBox["x1"]
                    or object.xPos > self.boundingBox["x2"]):
                if(object.type == "PLATFORM"):
                    global CRASHSPEED
                    self.collisionPartner = object
                    if self.fallSpeed <= CRASHSPEED:
                        return "LANDED"
                    else:
                        return "CRASHED"
                if (object.type == "LANDER"):
                    return "CRASHED"
        return "CLEAR"

    def DebugOut(self):
        print("fallspeed:\t%.2f" % self.fallSpeed)
        print("thrustpower:\t%.2f" % self.thrustPower)
        print("color:\t%s" % str(self.color))
        print("isThrustOn:\t%d" % self._isThrustOn)
        print("y-Position:\t%.2f" % self.yPos)
        print("x-Position:\t%.2f" % self.xPos)

    def drawLander(self, screen):
        if self.isAlive:
            pygame.draw.rect(screen, self.color, ((self.xPos, self.yPos), self.drawSize), 0)

    def clicked(self, mousePosition):
        if mousePosition[0] < self.xPos or mousePosition[0] > (self.xPos + self.drawSize[0]):
            return None
        if mousePosition[1] < self.yPos or mousePosition[1] > (self.yPos + self.drawSize[1]):
            return None
        self.thrust()

    def update(self, deltaTime, screen, log, objectList):
        crashed = False
        self.updateFallspeed(deltaTime)
        self.updateCoordinates(deltaTime)
        self.boundingBox = {"x1": self.xPos, "y1": self.yPos, "x2": (self.drawSize[0] + self.xPos), "y2": (self.drawSize[1] + self.yPos)}
        for object in objectList:
            result = self.checkCollision(object)
            if result != "CLEAR":
                self.isAlive = False
                if result == "LANDED":
                    self.hasScored = True
                if result == "CRASHED":
                    crashed = True
        self.drawLander(screen)


if __name__ == "__main__":
    DEBUGLEVEL = 2

    print("Start")
    time = 0.0
    deltaTime = 0.01
    myLander = Lander()
    while time < 2.0:
        myLander.updateFallspeed(deltaTime)
        myLander.updateCoordinates(deltaTime)
        if time >= 0.4:
            myLander.thrust()
        if time >= 1.6:
            myLander.unthrust()
        time += deltaTime
        if DEBUGLEVEL == 2:
            print("####%.2f####" % time)
            myLander.DebugOut()
        if DEBUGLEVEL == 1:
            print(myLander.yPos)
    print("Ende")
