from dataclasses import dataclass, field
from typing import NamedTuple
import math

from .state import CoshUI

# Holds data of individual particles and updates that data
class ParticleData:
    def __init__(self, position, color, speed, lifetime, direction):
        self.x, self.y = position
        self.color = color
        self.speed = speed
        self.lifetime = lifetime # the duration
        self.direction = direction # should already be randomized by spread inside ParticleManager._create_particle() call

        self.time = 0
        self._finished = False

    def _update(self, delta):
        if self._finished:
            return
        
        self.time += delta
        raw_t = min(self.time / self.lifetime, 1.0)

        rad = math.radians(self.direction)
        
        self.x += math.cos(rad) * self.speed * delta
        self.y += math.sin(rad) * self.speed * delta

        if raw_t >= 1.0:
            self._finished = True

@dataclass
class Particle:
    particle_data: dict[tuple, ParticleData] = field(default_factory=dict)
    z_index: int = 0

    def _update_all_particles(self, delta) -> bool:
        finished_particles = []
        for particle, data in self.particle_data.items():
            data._update(delta)
            if data._finished:
                finished_particles.append(particle)
        
        if not self.particle_data:
            return True
        return False

# Holds particle data and will be passed to the Render Stack
class ParticleContext(NamedTuple):
    particles: Particle | None = None
    z_index: int = 0

class ParticleManager:
    def __init__(self):
        self.particles: list[Particle] = []

    def update(self, delta):
        for particle in self.particles:
            particle._update_all_particles(delta)

    def _to_render_stack(self, particle: Particle):
        particle_context = ParticleContext(particle, particle.z_index)
        CoshUI._render_stack.append(particle_context)
    
    def _create_particle(self, position: tuple, speed: int | float, direction: int | float, count: int, lifetime: int, z_index: int, color: tuple):
        new_particle = Particle()
        new_particle.z_index = z_index

        for _ in range(count):
            data = ParticleData(position, color, speed, lifetime, direction)

            new_particle.particle_data.append(data)

        self.particles.append(new_particle)