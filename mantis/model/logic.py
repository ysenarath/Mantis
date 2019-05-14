from enum import Enum


class Message:
    class Type(Enum):
        ERROR = 0
        SUCCESS = 1

    def __init__(self, t, m):
        self.type = t
        self.text = m
