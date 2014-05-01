from optparse import _parse_int

__author__ = 'Simon'

import xml.etree.ElementTree as et
import os.path
import pygame

class Highscore(object):
    def __init__(self, highscoreFile):
        self.file = highscoreFile
        self.scores = list()
        self.initHighscores()

    def initHighscores(self):
        self.readHighscores()

    def dummyScores(self):
        return """
        <Highscore>
            <Entry no="1">
                <Name>Three</Name>
                <Score>1</Score>
            </Entry>
            <Entry no="2">
                <Name>Two</Name>
                <Score>2</Score>
            </Entry>
            <Entry no="3">
                <Name>One</Name>
                <Score>3</Score>
            </Entry>
        </Highscore>
        """

    def readHighscores(self):
        if os.path.exists(self.file):
            xmlRoot = et.parse(self.file)
        else:
            xmlRoot = et.fromstring(self.dummyScores())
        for en in xmlRoot.iter("Entry"):
            self.scores.append(self.xmlStringToNameScorePair(et.tostring(en)))

    def xmlStringToNameScorePair(self, entry):
        en = et.fromstring(entry)
        score = _parse_int(en.find("Score").text)
        name = en.find("Name").text
        return [name, score]


    def writeHighscores(self):
        xmlScores = et.Element("Highscore")
        count = 1
        for score in self.scores:
            entry = et.Element("Entry")
            entry.set("no", "%d" % count)
            count += 1
            xmlScores.append(entry)
            child = et.Element("Name")
            child.text = score[0]
            entry.append(child)
            child = et.Element("Score")
            child.text = str(score[1])
            entry.append(child)
        f = open(self.file, "w")
        f.write(et.tostring(xmlScores))
        f.close()

    def insertScore(self, **kwargs):
        scorePair = kwargs.get("scorePair", None)
        if scorePair != None:
            self.scores.append(scorePair)
        else:
            scorePair = [kwargs.get("name", ""), kwargs.get("score", -1)]
            self.scores.append(scorePair)
        self.scores = sorted(self.scores, key=lambda x: x[1], reverse=True)

    def drawHighscore(self, screen):
        for index, score in enumerate(self.scores):
            if index < 5:
                font = pygame.font.Font(None, 32)
                text = font.render("%03d" % score[1], True, (255, 255, 255))
                textRect = text.get_rect()
                textRect.x = 45
                textRect.y = 50 + 20 * index
                screen.blit(text, textRect)
                text = font.render("%s" % score[0], True, (255, 255, 255))
                textRect = text.get_rect()
                textRect.x = 130
                textRect.y = 50 + 20 * index
                screen.blit(text, textRect)


if __name__ == "__main__":
    myHigh = Highscore("test.xml")
    myHigh.writeHighscores()
    myHigh.drawHighscore("")
    myHigh.insertScore(name="ach", score=9)
    myHigh.drawHighscore("")
    myHigh.insertScore(scorePair=["ach", 19])
    myHigh.drawHighscore("")
