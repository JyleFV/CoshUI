from abc import ABC, abstractmethod

class CoshBackend(ABC):
    @abstractmethod
    def draw(self):
        pass

    def flush(self, render_stack : list):
        pass