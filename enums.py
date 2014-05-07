__author__ = 'Simon'


def enum(**enums):
    return type('Enum', (), enums)

GAMESTATE = enum(
    QUIT = "QUIT",
    RUNNING = "RUNNING",
    GAMEOVER = "GAMEOVER",
    TIMEUP = "TIMEUP",
    STARTSCREEN = "STARTSCREEN",
    HELPSCREEN = "HELPSCREEN"
)