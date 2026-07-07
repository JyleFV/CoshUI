from .state import CoshUI

# holds data of individual particles and updates that data
class ParticleData:
    pass

# Holds particle data and manages particle lifetime
class Particle:
    pass

class ParticleManager:
    def __init__(self):
        self.particles : list[Particle] = []

    def create_particle(self):
        pass

    def update(self):
        pass