"""
Chemanim Style - Scene Base Class
==================================

The ChemanimScene provides a themed base for all animations with:
- Automatic theme application
- Ambient particle backgrounds
- Styled title cards
- Signature intro/outro animations
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    class Scene:
        def construct(self): pass
        def add(self, *args): pass
        def play(self, *args): pass
        def wait(self, t=1): pass
    class VGroup:
        pass

import numpy as np
from typing import Optional
from .themes import ThemeConfig, CYBER_NEON, get_theme
from .colors import ChemanimColors
from .effects import ParticleField, GlassmorphismPanel


class ChemanimScene(Scene if MANIM_AVAILABLE else object):
    """
    Enhanced Scene class with Chemanim styling built-in.
    
    Features:
    - Themed backgrounds and colors
    - Ambient particle effects
    - Signature intro/outro
    - Easy access to styled elements
    
    Usage:
        class MyScene(ChemanimScene):
            theme = COSMIC_DUST  # or pass to set_theme()
            
            def construct(self):
                self.setup_theme()  # Optional if self.theme is set
                
                # Your content here
                title = self.create_title("My Animation")
                self.play_intro(title)
    """
    
    # Default theme - can be overridden in subclass
    theme: ThemeConfig = CYBER_NEON
    
    # Optional features
    enable_particles: bool = True
    enable_ambient_animation: bool = True
    
    def __init__(self, **kwargs):
        if not MANIM_AVAILABLE:
            return
        super().__init__(**kwargs)
        self._particles = None
        self._is_theme_setup = False
    
    def setup_theme(self, theme: Optional[ThemeConfig] = None):
        """
        Apply the theme to the scene.
        Call this at the start of construct() or it will be auto-called.
        """
        if not MANIM_AVAILABLE:
            return
            
        if theme:
            self.theme = theme
        
        # Set background
        self.camera.background_rgba = self._hex_to_rgba(self.theme.background_color)
        
        # Add ambient particles if enabled
        if self.enable_particles and self.theme.enable_particles:
            self._particles = ParticleField(
                colors=self.theme.particle_colors,
                num_particles=self.theme.particle_count // 2,  # Reduced for performance
                min_opacity=0.1,
                max_opacity=0.4,
            )
            self.add(self._particles)
            
            if self.enable_ambient_animation:
                self._particles.add_updater(
                    self._particles.get_drift_updater(speed=0.5)
                )
        
        self._is_theme_setup = True
    
    def set_theme(self, theme_name_or_config):
        """
        Set the theme by name or config object.
        
        Args:
            theme_name_or_config: Either a string like "cyber_neon" or a ThemeConfig
        """
        if isinstance(theme_name_or_config, str):
            self.theme = get_theme(theme_name_or_config)
        else:
            self.theme = theme_name_or_config
        
        if self._is_theme_setup:
            # Re-apply theme
            self.setup_theme()
    
    def construct(self):
        """Override in subclass. Theme is auto-setup if not done."""
        if not self._is_theme_setup:
            self.setup_theme()
    
    # ========================================================================
    # STYLED ELEMENT CREATORS
    # ========================================================================
    
    def create_title(self, text: str, gradient: bool = True):
        """Create a themed title."""
        if not MANIM_AVAILABLE:
            return VGroup()
        
        from .typography import GradientTitle, PremiumText
        
        if gradient:
            return GradientTitle(
                text,
                gradient_colors=[self.theme.primary, self.theme.secondary],
                font_size=72
            )
        else:
            return PremiumText(
                text,
                color=self.theme.text_primary,
                font_size=72,
                glow=True,
                glow_color=self.theme.glow_color
            )
    
    def create_subtitle(self, text: str):
        """Create a themed subtitle."""
        if not MANIM_AVAILABLE:
            return VGroup()
        
        from .typography import PremiumText
        
        return PremiumText(
            text,
            color=self.theme.text_secondary,
            font_size=36
        )
    
    def create_label(self, text: str, style: str = "neon"):
        """Create a themed label."""
        if not MANIM_AVAILABLE:
            return VGroup()
        
        from .typography import create_styled_label
        return create_styled_label(text, style=style, theme=self.theme)
    
    def create_panel(
        self, 
        width: float = 5, 
        height: float = 3,
        style: str = "glass"
    ):
        """Create a themed panel."""
        if not MANIM_AVAILABLE:
            return VGroup()
        
        from .effects import GlassmorphismPanel, HolographicPanel
        
        if style == "holographic":
            return HolographicPanel(
                width=width,
                height=height,
                primary_color=self.theme.primary,
                secondary_color=self.theme.secondary
            )
        else:
            return GlassmorphismPanel(
                width=width,
                height=height,
                fill_color=ChemanimColors.CARBON_GREY,
                fill_opacity=self.theme.glass_opacity,
                border_color=self.theme.primary,
                border_opacity=self.theme.glass_border_opacity,
                glow=self.theme.enable_glow,
                glow_color=self.theme.glow_color,
                glow_intensity=self.theme.glow_intensity * 0.5
            )
    
    # ========================================================================
    # SIGNATURE ANIMATIONS
    # ========================================================================
    
    def play_intro(self, title_mobject, with_particles: bool = True):
        """
        Play the signature Chemanim intro animation.
        
        Creates a stunning reveal for your title/main element.
        """
        if not MANIM_AVAILABLE:
            return
        
        from .animations import GlowFadeIn
        
        # Optional particle burst
        if with_particles and self.theme.enable_particles:
            from .effects import ParticleField
            burst = ParticleField(
                width=6,
                height=4,
                num_particles=30,
                colors=[self.theme.primary, self.theme.accent],
                max_opacity=0.8
            )
            burst.move_to(title_mobject.get_center())
            
            self.play(
                FadeIn(burst, run_time=0.5),
                GlowFadeIn(title_mobject, glow_color=self.theme.glow_color, run_time=1.5)
            )
            self.play(FadeOut(burst, run_time=0.5))
        else:
            self.play(
                GlowFadeIn(title_mobject, glow_color=self.theme.glow_color, run_time=1.5)
            )
    
    def play_outro(self, *mobjects):
        """
        Play the signature outro animation for given mobjects.
        """
        if not MANIM_AVAILABLE:
            return
        
        self.play(
            *[FadeOut(m, shift=UP * 0.5) for m in mobjects],
            run_time=1
        )
    
    def play_transition(self):
        """
        Play a transition effect between sections.
        """
        if not MANIM_AVAILABLE:
            return
        
        # Simple fade transition with pulse
        from .effects import NeonBorder
        
        flash = NeonBorder(
            width=16,
            height=9,
            color=self.theme.primary,
            intensity=0.5
        )
        
        self.play(
            FadeIn(flash, run_time=0.2),
            FadeOut(flash, run_time=0.3)
        )
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _hex_to_rgba(self, hex_color: str):
        """Convert hex color to RGBA tuple for camera background."""
        h = hex_color.lstrip('#')
        if len(h) == 8:  # Has alpha
            return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4, 6))
        return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1.0,)
    
    def get_theme_color(self, name: str) -> str:
        """Get a color from the current theme."""
        return getattr(self.theme, name, self.theme.primary)
    
    @property
    def primary_color(self):
        return self.theme.primary
    
    @property
    def secondary_color(self):
        return self.theme.secondary
    
    @property
    def accent_color(self):
        return self.theme.accent


# ============================================================================
# SPECIALIZED SCENE TYPES
# ============================================================================

class ChemanimMoleculeScene(ChemanimScene):
    """
    Scene specialized for molecular visualizations.
    
    Includes 3D camera setup and molecule-specific effects.
    """
    
    def setup(self):
        """Set up 3D camera for molecule viewing."""
        if not MANIM_AVAILABLE:
            return
        
        super().setup()
        
        # Configure camera for 3D
        self.camera.frame.set_euler_angles(
            theta=30 * DEGREES,
            phi=70 * DEGREES,
        )
        self.camera.frame.scale(1.2)
    
    def rotate_molecule(self, molecule, angle: float = TAU, run_time: float = 4):
        """Slowly rotate a molecule for visualization."""
        if not MANIM_AVAILABLE:
            return
        
        self.play(
            Rotate(molecule, angle=angle, axis=UP),
            run_time=run_time
        )


class ChemanimReactionScene(ChemanimScene):
    """
    Scene specialized for chemical reaction animations.
    """
    
    def play_reaction(self, reaction, run_time: float = 3):
        """Play a reaction with themed effects."""
        if not MANIM_AVAILABLE:
            return
        
        # Add energy glow during reaction
        from .effects import EnergyOrb
        
        energy = EnergyOrb(
            radius=0.3,
            core_color=self.theme.accent,
            halo_color=self.theme.primary
        )
        energy.move_to(ORIGIN)
        
        # Simplified - full implementation would coordinate with reaction
        self.play(
            FadeIn(energy, scale=2),
            run_time=run_time * 0.2
        )
        self.play(
            reaction.animate_reaction(run_time=run_time * 0.6)
        )
        self.play(
            FadeOut(energy),
            run_time=run_time * 0.2
        )
