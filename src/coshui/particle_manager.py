from dataclasses import dataclass, field
from typing import NamedTuple

from .state import CoshUI

# Holds data of individual particles and updates that data
class ParticleData:
    def __init__(self, position, color, speed, lifetime):
        self.position = position
        self.color = color
        self.speed = speed
        self.lifetime = lifetime

    def _update(self):
        pass

@dataclass
class Particle:
    particle_data: list[ParticleData] = field(default_factory=list)
    z_index: int = 0

    def _update(self):
        pass

# Holds particle data and will be passed to the Render Stack
class ParticleContext(NamedTuple):
    particles: Particle | None = None
    z_index: int = 0

class ParticleManager:
    def __init__(self):
        self.particles: list[Particle] = []

    def _create_particle(self, count: int, z_index: int):
        new_particle = Particle()
        new_particle.z_index = z_index

        for _ in range(count):
            data = ParticleData()

            new_particle.particle_data.append(data)

        self.particles.append(new_particle)

    def update(self):
        pass

    def _to_render_stack(self, particle):
        CoshUI._render_stack.append(ParticleContext(particles=particle))