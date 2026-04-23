from abc import ABC, abstractmethod

class CoshBackend(ABC):
    @abstractmethod
    def draw_rect(self):
        pass
    
    @abstractmethod
    def flush(self, render_stack : list):
        pass