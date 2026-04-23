from abc import ABC, abstractmethod

class CoshBackend(ABC):
    @abstractmethod
    def draw(self):
        pass

class PygameBackend(CoshBackend):
    def __init__(self, surface):
        self.surface = surface

    def draw(self):
        pass