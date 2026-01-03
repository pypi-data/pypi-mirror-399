"""
Chemanim Style - Visual Effects
================================

Premium visual effects including:
- Glassmorphism panels
- Neon glow effects
- Shimmer and sparkle effects
- Particle field systems
- Energy orbs and holographic elements

These effects differentiate Chemanim from standard Manim aesthetics.
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    # Minimal stubs for development
    class VGroup:
        def __init__(self, *args, **kwargs): pass
        def add(self, *mobject): return self
        def set_fill(self, *args, **kwargs): return self
        def set_stroke(self, *args, **kwargs): return self
        def move_to(self, point): return self
        def scale(self, factor): return self
        def shift(self, vector): return self
        def copy(self): return self
        def get_center(self): return [0, 0, 0]
    class VMobject(VGroup): pass
    class Rectangle(VGroup): pass
    class RoundedRectangle(VGroup): pass
    class Circle(VGroup): pass
    class Dot(VGroup): pass
    class Line(VGroup): pass
    
    import numpy as np
    UP = np.array([0, 1, 0])
    DOWN = np.array([0, -1, 0])
    LEFT = np.array([-1, 0, 0])
    RIGHT = np.array([1, 0, 0])
    ORIGIN = np.array([0, 0, 0])

import numpy as np
import random
from typing import Optional, List, Tuple, Union
from .colors import ChemanimColors, with_alpha, lighten


# ============================================================================
# GLASSMORPHISM EFFECTS
# ============================================================================

class GlassmorphismPanel(VGroup if MANIM_AVAILABLE else object):
    """
    A frosted-glass style panel with blur effect simulation.
    
    Creates a premium UI element with transparency, soft edges,
    and subtle gradient borders that simulate modern glass UI.
    """
    
    def __init__(
        self,
        width: float = 4,
        height: float = 3,
        corner_radius: float = 0.3,
        fill_color: str = ChemanimColors.CARBON_GREY,
        fill_opacity: float = 0.2,
        border_color: str = ChemanimColors.CYBER_CYAN,
        border_opacity: float = 0.5,
        border_width: float = 2,
        glow: bool = True,
        glow_color: Optional[str] = None,
        glow_intensity: float = 0.3,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        # Main glass panel
        self.panel = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=corner_radius,
        )
        self.panel.set_fill(fill_color, opacity=fill_opacity)
        self.panel.set_stroke(border_color, width=border_width, opacity=border_opacity)
        
        self.add(self.panel)
        
        # Optional glow effect
        if glow:
            glow_c = glow_color or border_color
            self.glow_layer = RoundedRectangle(
                width=width + 0.1,
                height=height + 0.1,
                corner_radius=corner_radius + 0.05,
            )
            self.glow_layer.set_fill(opacity=0)
            self.glow_layer.set_stroke(glow_c, width=border_width * 3, opacity=glow_intensity)
            self.add_to_back(self.glow_layer)
        
        # Inner highlight line (top edge gleam)
        self.highlight = Line(
            start=self.panel.get_corner(UL) + RIGHT * corner_radius + DOWN * 0.05,
            end=self.panel.get_corner(UR) + LEFT * corner_radius + DOWN * 0.05,
        )
        self.highlight.set_stroke(ChemanimColors.FROST_WHITE, width=1, opacity=0.3)
        self.add(self.highlight)


class HolographicPanel(VGroup if MANIM_AVAILABLE else object):
    """
    A holographic/sci-fi style panel with gradient borders and scan lines.
    """
    
    def __init__(
        self,
        width: float = 5,
        height: float = 3,
        primary_color: str = ChemanimColors.CYBER_CYAN,
        secondary_color: str = ChemanimColors.PLASMA_MAGENTA,
        corner_radius: float = 0.2,
        scanlines: bool = True,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
        
        super().__init__(**kwargs)
        
        # Main panel with gradient border effect (simulated with multiple strokes)
        self.outer = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=corner_radius,
        )
        self.outer.set_fill(ChemanimColors.DEEP_SPACE, opacity=0.8)
        self.outer.set_stroke(primary_color, width=3, opacity=0.8)
        
        # Inner border for depth
        self.inner = RoundedRectangle(
            width=width - 0.15,
            height=height - 0.15,
            corner_radius=corner_radius - 0.05,
        )
        self.inner.set_fill(opacity=0)
        self.inner.set_stroke(secondary_color, width=1, opacity=0.5)
        
        self.add(self.outer, self.inner)
        
        # Add scan lines for holographic effect
        if scanlines:
            self._add_scanlines(width, height, primary_color)
    
    def _add_scanlines(self, width: float, height: float, color: str):
        """Add horizontal scan lines."""
        num_lines = int(height / 0.15)
        for i in range(num_lines):
            y_pos = -height/2 + 0.1 + i * (height - 0.2) / num_lines
            line = Line(
                start=LEFT * (width/2 - 0.15),
                end=RIGHT * (width/2 - 0.15),
            ).shift(UP * y_pos)
            line.set_stroke(color, width=0.5, opacity=0.1)
            self.add(line)


# ============================================================================
# GLOW EFFECTS
# ============================================================================

class GlowEffect(VGroup if MANIM_AVAILABLE else object):
    """
    Add a neon glow effect around any mobject.
    
    Creates multiple copies with increasing blur/opacity falloff
    to simulate a soft glow.
    """
    
    def __init__(
        self,
        mobject,
        color: str = ChemanimColors.CYBER_CYAN,
        intensity: float = 0.5,
        layers: int = 5,
        spread: float = 0.03,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        # Create glow layers (outer to inner)
        for i in range(layers, 0, -1):
            layer = mobject.copy()
            scale_factor = 1 + spread * i
            layer.scale(scale_factor)
            opacity = intensity * (layers - i + 1) / layers * 0.5
            layer.set_stroke(color, width=2 * i, opacity=opacity)
            layer.set_fill(opacity=0)
            self.add(layer)
        
        # Add the original mobject on top
        self.add(mobject)


class NeonBorder(VGroup if MANIM_AVAILABLE else object):
    """
    A neon-lit border effect for rectangles.
    """
    
    def __init__(
        self,
        width: float = 4,
        height: float = 2,
        color: str = ChemanimColors.CYBER_CYAN,
        intensity: float = 0.8,
        flicker: bool = False,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        # Outer glow
        self.glow_outer = Rectangle(width=width + 0.15, height=height + 0.15)
        self.glow_outer.set_fill(opacity=0)
        self.glow_outer.set_stroke(color, width=12, opacity=intensity * 0.2)
        
        # Middle glow
        self.glow_mid = Rectangle(width=width + 0.08, height=height + 0.08)
        self.glow_mid.set_fill(opacity=0)
        self.glow_mid.set_stroke(color, width=6, opacity=intensity * 0.4)
        
        # Core line
        self.core = Rectangle(width=width, height=height)
        self.core.set_fill(opacity=0)
        self.core.set_stroke(lighten(color, 0.3), width=2, opacity=intensity)
        
        self.add(self.glow_outer, self.glow_mid, self.core)


# ============================================================================
# PARTICLE EFFECTS
# ============================================================================

class ParticleField(VGroup if MANIM_AVAILABLE else object):
    """
    A field of floating particles for ambient background effects.
    
    Great for creating atmospheric molecular/quantum visualizations.
    """
    
    def __init__(
        self,
        width: float = 14,
        height: float = 8,
        num_particles: int = 50,
        colors: Optional[List[str]] = None,
        min_size: float = 0.02,
        max_size: float = 0.08,
        min_opacity: float = 0.2,
        max_opacity: float = 0.8,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        colors = colors or [
            ChemanimColors.CYBER_CYAN,
            ChemanimColors.PLASMA_MAGENTA,
            ChemanimColors.NEON_GREEN,
            ChemanimColors.SOLAR_GOLD,
        ]
        
        self.particles = []
        
        for _ in range(num_particles):
            x = random.uniform(-width/2, width/2)
            y = random.uniform(-height/2, height/2)
            size = random.uniform(min_size, max_size)
            opacity = random.uniform(min_opacity, max_opacity)
            color = random.choice(colors)
            
            particle = Dot(radius=size)
            particle.set_fill(color, opacity=opacity)
            particle.set_stroke(color, width=0.5, opacity=opacity * 0.5)
            particle.move_to([x, y, 0])
            
            self.particles.append(particle)
            self.add(particle)
    
    def get_drift_updater(self, speed: float = 0.02, bounds: Tuple[float, float] = (-7, 7)):
        """Return an updater function for gentle particle drifting."""
        def updater(m, dt):
            for p in self.particles:
                # Random gentle drift
                drift = np.array([
                    random.uniform(-1, 1) * speed * dt,
                    random.uniform(-1, 1) * speed * dt,
                    0
                ])
                new_pos = p.get_center() + drift
                
                # Wrap around bounds
                for i in range(2):
                    if new_pos[i] < bounds[0]:
                        new_pos[i] = bounds[1]
                    elif new_pos[i] > bounds[1]:
                        new_pos[i] = bounds[0]
                
                p.move_to(new_pos)
        return updater


class EnergyOrb(VGroup if MANIM_AVAILABLE else object):
    """
    A glowing energy orb with pulsing core and particle halo.
    
    Perfect for representing atoms, energy states, or reaction centers.
    """
    
    def __init__(
        self,
        radius: float = 0.5,
        core_color: str = ChemanimColors.SOLAR_GOLD,
        halo_color: str = ChemanimColors.CYBER_CYAN,
        glow_layers: int = 4,
        particle_count: int = 12,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        # Outer glow layers
        for i in range(glow_layers, 0, -1):
            glow = Circle(radius=radius * (1 + i * 0.3))
            opacity = 0.15 / i
            glow.set_fill(halo_color, opacity=opacity)
            glow.set_stroke(opacity=0)
            self.add(glow)
        
        # Core orb
        self.core = Circle(radius=radius)
        self.core.set_fill(core_color, opacity=0.9)
        self.core.set_stroke(lighten(core_color, 0.3), width=2)
        self.add(self.core)
        
        # Inner bright spot
        inner = Circle(radius=radius * 0.3)
        inner.set_fill(ChemanimColors.FROST_WHITE, opacity=0.6)
        inner.set_stroke(opacity=0)
        inner.shift(UP * radius * 0.2 + LEFT * radius * 0.1)
        self.add(inner)
        
        # Orbital particles
        for i in range(particle_count):
            angle = 2 * np.pi * i / particle_count
            dist = radius * 1.5
            particle = Dot(radius=0.03)
            particle.set_fill(halo_color, opacity=0.7)
            particle.move_to([np.cos(angle) * dist, np.sin(angle) * dist, 0])
            self.add(particle)


class ShimmerEffect:
    """
    Creates a shimmer/sparkle effect that can be applied to mobjects.
    
    Returns an updater function that makes elements glitter.
    """
    
    @staticmethod
    def create_updater(
        colors: Optional[List[str]] = None,
        speed: float = 2.0,
        intensity: float = 0.3
    ):
        """
        Create a shimmer updater that varies stroke opacity.
        """
        colors = colors or [ChemanimColors.CYBER_CYAN, ChemanimColors.FROST_WHITE]
        
        def updater(m, dt):
            import time
            t = time.time() * speed
            # Vary opacity with sine wave
            opacity = 0.5 + intensity * np.sin(t)
            m.set_stroke(opacity=opacity)
        
        return updater


# ============================================================================
# MOLECULE-SPECIFIC EFFECTS
# ============================================================================

class ElectronCloud(VGroup if MANIM_AVAILABLE else object):
    """
    A fuzzy electron cloud visualization around atoms.
    """
    
    def __init__(
        self,
        atom_position: np.ndarray = ORIGIN if MANIM_AVAILABLE else np.array([0,0,0]),
        radius: float = 1.0,
        density: int = 20,
        color: str = ChemanimColors.ELECTRIC_VIOLET,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(**kwargs)
        
        # Create probability density cloud with random dots
        for _ in range(density):
            # Gaussian distribution around center
            r = abs(np.random.normal(0, radius * 0.4))
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi)
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)
            
            # Size and opacity based on distance from center
            size = 0.02 + 0.03 * (1 - r / radius)
            opacity = 0.3 * (1 - r / (radius * 1.5))
            
            dot = Dot(radius=size)
            dot.set_fill(color, opacity=max(0.1, opacity))
            dot.move_to(atom_position + np.array([x, y, z]))
            self.add(dot)


class BondGlow(Line if MANIM_AVAILABLE else object):
    """
    A glowing chemical bond with energy flow effect.
    """
    
    def __init__(
        self,
        start,
        end,
        color: str = ChemanimColors.NEON_GREEN,
        glow_intensity: float = 0.5,
        **kwargs
    ):
        if not MANIM_AVAILABLE:
            return
            
        super().__init__(start, end, **kwargs)
        
        # Set core line
        self.set_stroke(lighten(color, 0.2), width=3)
        
        # This is a simplified version - full implementation would
        # add multiple glow layers as separate mobjects


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def apply_glow(mobject, color: str = ChemanimColors.CYBER_CYAN, intensity: float = 0.5):
    """Apply a glow effect to an existing mobject."""
    return GlowEffect(mobject, color=color, intensity=intensity)


def create_ambient_particles(theme_config) -> ParticleField:
    """Create a particle field using theme settings."""
    return ParticleField(
        colors=theme_config.particle_colors,
        num_particles=theme_config.particle_count,
    )
