"""
Chemanim Style Add-on
=====================

A premium visual styling library for ManimGL, featuring:
- Exclusive color palettes (differentiating from 3Blue1Brown)
- Glassmorphism effects
- Neon glow and shimmer effects
- Particle animations
- Premium typography
- Signature animations

Usage:
    from chemanim.style import *
    
    class MyScene(ChemanimScene):
        def construct(self):
            self.set_theme(CYBER_NEON)  # or AURORA_GLOW, QUANTUM_FROST, etc.
            ...

Author: Chemanim
License: MIT
"""

from .colors import *
from .themes import *
from .effects import *
from .animations import *
from .typography import *
from .scene import ChemanimScene
from .presets import *

__version__ = "1.0.0"
__all__ = [
    # Core
    "ChemanimScene",
    
    # Themes
    "CYBER_NEON", "AURORA_GLOW", "QUANTUM_FROST", "SOLAR_FLARE", 
    "DEEP_OCEAN", "COSMIC_DUST", "EMERALD_MATRIX", "ROYAL_VELVET",
    
    # Color Palettes
    "ChemanimColors", "GradientPalette",
    
    # Effects
    "GlowEffect", "GlassmorphismPanel", "NeonText", "ShimmerEffect",
    "ParticleField", "EnergyOrb", "HolographicPanel",
    
    # Animations
    "NeonWrite", "GlowFadeIn", "ParticleAssemble", "ShimmerIn",
    "PulseHighlight", "EnergyFlow", "QuantumTeleport", "HolographicReveal",
    
    # Typography
    "PremiumText", "GradientTitle", "NeonLabel", "HolographicText",
    
    # Presets
    "create_styled_molecule", "create_styled_reaction",
    "create_styled_protein", "apply_premium_style",
]
