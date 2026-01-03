"""
Chemanim Style - Premium Animations
====================================

Signature animation effects that differentiate Chemanim from standard Manim.
Includes:
- NeonWrite: Glowing text reveal
- GlowFadeIn: Fade in with expanding glow
- ParticleAssemble: Objects form from particles
- ShimmerIn: Shimmering reveal effect
- PulseHighlight: Pulsing attention grabber
- EnergyFlow: Flowing energy along paths
- QuantumTeleport: Quantum-style teleportation
- HolographicReveal: Sci-fi hologram appearance
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    # Stub for Animation
    class Animation:
        def __init__(self, *args, **kwargs): pass
    class Transform(Animation): pass
    class FadeIn(Animation): pass
    class Write(Animation): pass
    class VGroup:
        pass

import numpy as np
from typing import Optional, List, Callable
from .colors import ChemanimColors, lighten, with_alpha


# ============================================================================
# NEON WRITE ANIMATION
# ============================================================================

if MANIM_AVAILABLE:
    class NeonWrite(Write):
        """
        Write animation with neon glow effect.
        Text appears with a glowing trail.
        """
        
        def __init__(
            self,
            mobject,
            glow_color: str = ChemanimColors.CYBER_CYAN,
            glow_width: float = 8,
            **kwargs
        ):
            # Store original stroke
            self._original_stroke = mobject.get_stroke_width()
            self._original_color = mobject.get_stroke_color()
            self.glow_color = glow_color
            self.glow_width = glow_width
            
            # Make mobject glow during write
            mobject.set_stroke(glow_color, width=glow_width)
            
            super().__init__(mobject, **kwargs)
        
        def finish(self):
            super().finish()
            # Restore to normal after animation
            self.mobject.set_stroke(
                self._original_color, 
                width=self._original_stroke
            )


    class GlowFadeIn(FadeIn):
        """
        Fade in with an expanding glow effect that settles.
        """
        
        def __init__(
            self,
            mobject,
            glow_color: Optional[str] = None,
            glow_scale: float = 1.5,
            **kwargs
        ):
            self.glow_color = glow_color or ChemanimColors.CYBER_CYAN
            self.glow_scale = glow_scale
            super().__init__(mobject, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            super().interpolate_mobject(alpha)
            
            # Glow expands out then settles
            glow_alpha = 1 - abs(2 * alpha - 1)  # Peaks at alpha=0.5
            scale = 1 + (self.glow_scale - 1) * glow_alpha
            
            self.mobject.set_stroke(
                self.glow_color,
                width=4 * glow_alpha,
                opacity=0.5 * glow_alpha
            )


# ============================================================================
# PARTICLE ASSEMBLY ANIMATION
# ============================================================================

if MANIM_AVAILABLE:
    class ParticleAssemble(Animation):
        """
        Object forms from scattered particles flying together.
        
        Creates a stunning effect where particles converge to form the shape.
        """
        
        def __init__(
            self,
            mobject,
            num_particles: int = 50,
            particle_color: Optional[str] = None,
            scatter_radius: float = 5,
            **kwargs
        ):
            self.num_particles = num_particles
            self.particle_color = particle_color or ChemanimColors.CYBER_CYAN
            self.scatter_radius = scatter_radius
            self.particles = VGroup()
            self.target_points = []
            
            # Create particles at random positions
            for _ in range(num_particles):
                angle = np.random.uniform(0, 2 * np.pi)
                dist = np.random.uniform(scatter_radius * 0.5, scatter_radius)
                
                particle = Dot(radius=0.03)
                particle.set_fill(self.particle_color, opacity=0.8)
                particle.move_to([
                    np.cos(angle) * dist,
                    np.sin(angle) * dist,
                    np.random.uniform(-0.5, 0.5)
                ])
                self.particles.add(particle)
                
                # Random point on target mobject
                self.target_points.append(mobject.point_from_proportion(
                    np.random.uniform(0, 1)
                ))
            
            super().__init__(self.particles, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            # Ease in-out for smooth motion
            eased_alpha = (1 - np.cos(alpha * np.pi)) / 2
            
            for i, particle in enumerate(self.particles):
                start = particle.get_center()
                end = self.target_points[i]
                
                # Move towards target
                new_pos = start + (end - start) * eased_alpha
                particle.move_to(new_pos)
                
                # Fade out as it reaches target
                if alpha > 0.7:
                    fade = (1 - alpha) / 0.3
                    particle.set_opacity(fade)


# ============================================================================
# SHIMMER ANIMATION
# ============================================================================

if MANIM_AVAILABLE:
    class ShimmerIn(Animation):
        """
        Reveal with a shimmering/sparkling effect.
        """
        
        def __init__(
            self,
            mobject,
            shimmer_color: str = ChemanimColors.SOLAR_GOLD,
            shimmer_waves: int = 3,
            **kwargs
        ):
            self.shimmer_color = shimmer_color
            self.shimmer_waves = shimmer_waves
            self.original_opacity = mobject.get_fill_opacity()
            mobject.set_opacity(0)
            super().__init__(mobject, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            # Base reveal
            self.mobject.set_opacity(alpha * self.original_opacity)
            
            # Shimmer overlay (sine wave along progress)
            shimmer = np.sin(alpha * np.pi * self.shimmer_waves)
            
            if shimmer > 0:
                self.mobject.set_stroke(
                    self.shimmer_color,
                    width=2 * shimmer,
                    opacity=0.5 * shimmer
                )
            else:
                self.mobject.set_stroke(width=0)


# ============================================================================
# PULSE HIGHLIGHT ANIMATION  
# ============================================================================

if MANIM_AVAILABLE:
    class PulseHighlight(Animation):
        """
        Draw attention with pulsing glow effect.
        """
        
        def __init__(
            self,
            mobject,
            pulse_color: str = ChemanimColors.NEON_GREEN,
            num_pulses: int = 2,
            scale_factor: float = 1.1,
            **kwargs
        ):
            self.pulse_color = pulse_color
            self.num_pulses = num_pulses
            self.scale_factor = scale_factor
            self.original_scale = 1.0
            super().__init__(mobject, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            # Multiple pulses over duration
            pulse_phase = (alpha * self.num_pulses) % 1
            pulse_intensity = np.sin(pulse_phase * np.pi)
            
            # Scale pulse
            current_scale = 1 + (self.scale_factor - 1) * pulse_intensity
            # Note: This is simplified - full impl would track original scale
            
            # Glow pulse
            self.mobject.set_stroke(
                self.pulse_color,
                width=4 * pulse_intensity,
                opacity=0.7 * pulse_intensity
            )


# ============================================================================
# ENERGY FLOW ANIMATION
# ============================================================================

if MANIM_AVAILABLE:
    class EnergyFlow(Animation):
        """
        Animated energy flowing along a path (e.g., along bonds).
        """
        
        def __init__(
            self,
            path_mobject,
            flow_color: str = ChemanimColors.SOLAR_GOLD,
            trail_length: float = 0.2,
            num_particles: int = 5,
            **kwargs
        ):
            self.path = path_mobject
            self.flow_color = flow_color
            self.trail_length = trail_length
            
            # Create flowing particles
            self.flow_particles = VGroup(*[
                Dot(radius=0.04).set_fill(flow_color, opacity=0.8)
                for _ in range(num_particles)
            ])
            
            super().__init__(self.flow_particles, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            num_p = len(self.flow_particles)
            
            for i, particle in enumerate(self.flow_particles):
                # Stagger particles along path
                offset = i / num_p * 0.3
                position = (alpha + offset) % 1
                
                # Get point on path
                point = self.path.point_from_proportion(position)
                particle.move_to(point)
                
                # Fade based on position in trail
                opacity = 0.8 - 0.6 * (i / num_p)
                particle.set_opacity(opacity)


# ============================================================================
# QUANTUM TELEPORT ANIMATION
# ============================================================================

if MANIM_AVAILABLE:
    class QuantumTeleport(Animation):
        """
        Quantum-style disappear/reappear with probability cloud effect.
        """
        
        def __init__(
            self,
            mobject,
            target_position,
            cloud_color: str = ChemanimColors.ELECTRIC_VIOLET,
            **kwargs
        ):
            self.start_pos = mobject.get_center().copy()
            self.target_pos = np.array(target_position)
            self.cloud_color = cloud_color
            super().__init__(mobject, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            if alpha < 0.4:
                # Phase 1: Dematerializing (fuzz out)
                phase_alpha = alpha / 0.4
                self.mobject.set_opacity(1 - phase_alpha)
                # Could add fuzzing effect here
                
            elif alpha < 0.6:
                # Phase 2: Invisible transit
                self.mobject.set_opacity(0)
                
            else:
                # Phase 3: Rematerializing at target
                phase_alpha = (alpha - 0.6) / 0.4
                self.mobject.move_to(self.target_pos)
                self.mobject.set_opacity(phase_alpha)


# ============================================================================
# HOLOGRAPHIC REVEAL
# ============================================================================

if MANIM_AVAILABLE:
    class HolographicReveal(Animation):
        """
        Sci-fi style hologram appearance with scan lines.
        """
        
        def __init__(
            self,
            mobject,
            holo_color: str = ChemanimColors.CYBER_CYAN,
            scan_speed: float = 2,
            **kwargs
        ):
            self.holo_color = holo_color
            self.scan_speed = scan_speed
            self.original_colors = None  # Would store original colors
            super().__init__(mobject, **kwargs)
        
        def interpolate_mobject(self, alpha: float):
            # Holographic tint during reveal
            if alpha < 0.8:
                # Still in hologram mode
                self.mobject.set_fill(self.holo_color, opacity=alpha * 0.5)
                self.mobject.set_stroke(self.holo_color, opacity=alpha)
                
                # Flicker effect
                flicker = 0.3 * np.sin(alpha * self.scan_speed * np.pi * 10)
                self.mobject.set_opacity(alpha * 0.7 + flicker)
            else:
                # Transition to solid
                transition = (alpha - 0.8) / 0.2
                self.mobject.set_opacity(0.7 + 0.3 * transition)


# ============================================================================
# ANIMATION UTILITIES
# ============================================================================

def create_staggered_animation(
    mobjects: List,
    animation_class,
    lag_ratio: float = 0.1,
    **kwargs
) -> "AnimationGroup":
    """
    Create staggered animations for a list of mobjects.
    """
    if not MANIM_AVAILABLE:
        return None
    
    return AnimationGroup(
        *[animation_class(m, **kwargs) for m in mobjects],
        lag_ratio=lag_ratio
    )


def apply_signature_intro(mobject, theme=None):
    """
    Get the signature Chemanim intro animation sequence.
    Returns a list of animations to play.
    """
    if not MANIM_AVAILABLE:
        return []
    
    color = theme.primary if theme else ChemanimColors.CYBER_CYAN
    
    return [
        GlowFadeIn(mobject, glow_color=color, run_time=1.5),
    ]
