from abc import ABC, abstractmethod

class CoshBackend(ABC):
    @abstractmethod
    def _draw_rect(self):
        pass

    @abstractmethod
    def _draw_text(self):
        pass

    @abstractmethod
    def _draw_image(self):
        pass
    
    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def poll_input(self):
        pass