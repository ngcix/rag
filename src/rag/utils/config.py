
from enum import IntEnum

class DebugLevel(IntEnum):
    NONE = 0
    DEBUG = 1
    VERBOSE = 2

class Config:
    def __init__(self):
        self.debugLevel = DebugLevel.NONE

_config = Config()

def getConfig():
    return _config
