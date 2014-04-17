__author__ = 'Simon'

import random
import pygame
GRAVITY = 15  # 9.98 # Earth value
CRASHSPEED = 40.0


class Lander(object):
    def __init__(self, parent, landerList, platformList, thrustPower=25.0):
        self.parent = parent
        self.fallSpeed = 0
        self.thrustPower = thrustPower
        self.yPos = None
        self.xPos = None
        self.color = None
        self.isThrustOn = False
        self.horizontalSpeed = 0.0
        self.drawSize = (40, 40)
        self.isAlive = True
        self.type = "LANDER"
        self.hasScored = False
        self.hasCrashed = False
        self.collisionPartner = None
        self.boundingBox = {"x1": 0, "x2": 0, "y1": 0, "y2": 0}
        self.horizontalThrustLeftOn = False
        self.horizontalThrustRightOn = False
        self.landerList = landerList
        self.platformList = platformList
        self.fuelLeft = 10
        # call spawn to set position and color with collision check before spawning lander
        self.spawn(0)

    def spawn(self, tries):
        if tries > 5:
            self.isAlive = False
        else:
            self.yPos = 0
            self.color = ((255, 0, 0), (0, 0, 255), (255, 255, 0))[random.randint(0, 2)]
            self.xPos = random.randrange(10, 280)
            self.calcBoundingBox()
            for lander in self.landerList:
                if self.checkCollision(lander) != "CLEAR":
                    self.spawn(tries+1)


    def thrust(self):
        if self.fuelLeft > 0:
            self.isThrustOn = True


    def unthrust(self):
        self.isThrustOn = False

    def horizontalThrust(self, direction):
        self.horizontalThrustLeftOn = direction == "LEFT"
        self.horizontalThrustRightOn = direction == "RIGHT"

    def horizontalUnthrust(self):
        self.horizontalThrustLeftOn = False
        self.horizontalThrustRightOn = False

    def updateFallspeed(self, deltaTime):
        global GRAVITY
        self.fallSpeed += ((GRAVITY - (self.thrustPower * self.isThrustOn)) * deltaTime)
        if self.yPos <= 0.5:
            self.fallSpeed = max(0, self.fallSpeed)
        self.horizontalSpeed += ((self.thrustPower * -self.horizontalThrustLeftOn) + (self.thrustPower * self.horizontalThrustRightOn)) * deltaTime
        self.horizontalSpeed -= (0.5 * self.horizontalSpeed) * deltaTime

    def updateCoordinates(self, deltaTime):
        self.xPos += (self.horizontalSpeed * deltaTime)
        self.xPos %= 310
        self.yPos = max(self.yPos + (self.fallSpeed * deltaTime), 0)


    def checkCollision(self, object):
        if object == self or not object.isAlive:
            return "CLEAR"
        if self.yPos > self.parent.drawSize[1]:  # replace with screen size height
            self.collisionPartner = "EDGE"
            return "CRASHED"
        if not((object.yPos + object.drawSize[1]) < self.boundingBox["y1"]
                or object.yPos > self.boundingBox["y2"]):
            if not((object.xPos + object.drawSize[0]) < self.boundingBox["x1"]
                    or object.xPos > self.boundingBox["x2"]):
                if object.type == "PLATFORM":
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
        print("isThrustOn:\t%d" % self.isThrustOn)
        print("y-Position:\t%.2f" % self.yPos)
        print("x-Position:\t%.2f" % self.xPos)

    def drawLander(self, screen, assets):
        if self.isAlive:
            global CRASHSPEED
            fallSpeedLight = (assets.landerLightRed if self.fallSpeed >= CRASHSPEED else assets.landerLightGreen)
            box = None
            if self.color == (255, 0, 0):
                box = assets.redBox
            elif self.color == (255, 255, 0):
                box = assets.yellowBox
            elif self.color == (0, 0, 255):
                box = assets.blueBox
            screen.blit(box, (self.xPos, self.yPos))
            screen.blit(assets.boxOverlay, (self.xPos, self.yPos))
            screen.blit(assets.landerBody, (self.xPos, self.yPos))
            screen.blit(assets.rotorA, (self.xPos, self.yPos))
            screen.blit(fallSpeedLight, (self.xPos, self.yPos))
            fuelBarColor = (0, 255, 0)
            relativeFuel = (self.fuelLeft / 10)
            if relativeFuel < 0.9:
                fuelBarColor = (255, 255, 0)
            if relativeFuel < 0.4:
                fuelBarColor = (255, 0, 0)
            pygame.draw.rect(screen, (0, 0, 0), ((self.xPos, self.yPos), (4, 20)), 0)
            pygame.draw.rect(screen, fuelBarColor, ((self.xPos+1, self.yPos), (2, 20 * relativeFuel)), 0)

    def clicked(self, mousePosition):
        if mousePosition[0] < self.xPos or mousePosition[0] > (self.xPos + self.drawSize[0]):
            return None
        if mousePosition[1] < self.yPos or mousePosition[1] > (self.yPos + self.drawSize[1]):
            return None
        self.thrust()

    def calcBoundingBox(self):
        self.boundingBox = {"x1": self.xPos, "y1": self.yPos, "x2": (self.drawSize[0] + self.xPos), "y2": (self.drawSize[1] + self.yPos)}

    def useFuel(self, deltaTime):
        if self.isThrustOn:
            self.fuelLeft -= deltaTime
        if self.fuelLeft <= 0:
            self.unthrust()

    def update(self, deltaTime, screen, assets, log):
        self.updateFallspeed(deltaTime)
        self.updateCoordinates(deltaTime)
        self.calcBoundingBox()
        self.useFuel(deltaTime)
        objectList = (self.landerList + self.platformList)
        for object in objectList:
            result = self.checkCollision(object)
            if result != "CLEAR":
                self.isAlive = False
                if result == "LANDED":
                    self.hasScored = True
                if result == "CRASHED":
                    self.hasCrashed = True
        self.drawLander(screen, assets)

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
