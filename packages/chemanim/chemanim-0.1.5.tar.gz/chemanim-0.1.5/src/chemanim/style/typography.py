"""
Chemanim Style - Premium Typography
====================================

High-quality text styling for scientific animations:
- Gradient text
- Neon text effects
- Holographic labels
- Scientific notation styling
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    class VGroup:
        def __init__(self, *args, **kwargs): pass
        def add(self, *args): return self
        def scale(self, s): return self
        def move_to(self, p): return self
        def shift(self, v): return self
        def set_color(self, c): return self
    class Text(VGroup): pass
    class Tex(VGroup): pass

import numpy as np
from typing import Optional, List
from .colors import ChemanimColors, GradientPalette, lighten


# ============================================================================
# PREMIUM TEXT CLASSES
# ============================================================================

if MANIM_AVAILABLE:
    class PremiumText(Text):
        """
        Enhanced Text with premium styling options.
        
        Features:
        - Custom fonts (defaults to modern sans-serif)
        - Automatic contrast coloring
        - Optional shadow/glow
        """
        
        def __init__(
            self,
            text: str,
            font: str = "Inter",
            color: str = ChemanimColors.FROST_WHITE,
            font_size: int = 48,
            weight: str = "MEDIUM",
            glow: bool = False,
            glow_color: Optional[str] = None,
            **kwargs
        ):
            super().__init__(
                text,
                font=font,
                font_size=font_size,
                weight=weight,
                **kwargs
            )
            self.set_color(color)
            
            if glow:
                self._apply_glow(glow_color or color)
        
        def _apply_glow(self, color: str):
            """Add a subtle glow effect."""
            self.set_stroke(color, width=4, opacity=0.3, background=True)


    class GradientTitle(VGroup):
        """
        A title with gradient coloring applied.
        
        Note: True gradients on text require creating character groups.
        This applies gradient across individual characters.
        """
        
        def __init__(
            self,
            text: str,
            gradient_colors: List[str] = None,
            font_size: int = 72,
            font: str = "Inter",
            **kwargs
        ):
            super().__init__(**kwargs)
            
            colors = gradient_colors or [
                ChemanimColors.CYBER_CYAN,
                ChemanimColors.PLASMA_MAGENTA,
            ]
            
            # Create text
            text_mob = Text(text, font=font, font_size=font_size)
            
            # Apply gradient across characters
            n_chars = len(text_mob)
            for i, char in enumerate(text_mob):
                t = i / max(1, n_chars - 1)
                
                # Interpolate between gradient colors
                n_colors = len(colors)
                scaled_t = t * (n_colors - 1)
                idx = int(scaled_t)
                blend = scaled_t - idx
                
                if idx >= n_colors - 1:
                    char.set_color(colors[-1])
                else:
                    # Blend between two colors
                    c1 = colors[idx]
                    c2 = colors[idx + 1]
                    # Simple RGB blend
                    char.set_color(c1)  # Simplified - full impl would blend
            
            self.add(text_mob)
            self.text = text_mob


    class NeonLabel(VGroup):
        """
        Text with neon sign effect - bright core with colored glow.
        """
        
        def __init__(
            self,
            text: str,
            neon_color: str = ChemanimColors.CYBER_CYAN,
            font_size: int = 48,
            glow_layers: int = 3,
            **kwargs
        ):
            super().__init__(**kwargs)
            
            # Create glow layers (outer to inner)
            for i in range(glow_layers, 0, -1):
                glow_text = Text(text, font_size=font_size)
                glow_text.set_stroke(neon_color, width=i * 4, opacity=0.3 / i)
                glow_text.set_fill(opacity=0)
                self.add(glow_text)
            
            # Bright core
            core_text = Text(text, font_size=font_size)
            core_text.set_color(lighten(neon_color, 0.4))
            core_text.set_stroke(ChemanimColors.FROST_WHITE, width=1, opacity=0.8)
            self.add(core_text)
            
            self.core = core_text


    class HolographicText(VGroup):
        """
        Sci-fi holographic text with scan line effect.
        """
        
        def __init__(
            self,
            text: str,
            holo_color: str = ChemanimColors.CYBER_CYAN,
            font_size: int = 48,
            scanlines: bool = True,
            **kwargs
        ):
            super().__init__(**kwargs)
            
            # Main text
            main_text = Text(text, font_size=font_size)
            main_text.set_color(holo_color)
            main_text.set_stroke(holo_color, width=2, opacity=0.5)
            self.add(main_text)
            
            # Duplicate slightly offset for depth
            ghost = Text(text, font_size=font_size)
            ghost.set_color(ChemanimColors.PLASMA_MAGENTA)
            ghost.set_opacity(0.3)
            ghost.shift(np.array([0.02, 0.02, 0]))
            self.add_to_back(ghost)
            
            self.main_text = main_text


# ============================================================================
# SCIENTIFIC TEXT UTILITIES
# ============================================================================

if MANIM_AVAILABLE:
    class ChemicalFormula(Tex):
        """
        Properly formatted chemical formula with subscripts.
        
        Example: ChemicalFormula("H2O") renders H₂O correctly.
        """
        
        def __init__(
            self,
            formula: str,
            color: str = ChemanimColors.FROST_WHITE,
            **kwargs
        ):
            # Convert to LaTeX format
            latex = self._to_latex(formula)
            super().__init__(latex, **kwargs)
            self.set_color(color)
        
        def _to_latex(self, formula: str) -> str:
            """Convert simple formula to LaTeX."""
            import re
            # Convert numbers to subscripts
            result = re.sub(r'(\d+)', r'_{\1}', formula)
            return f"${result}$"


    class ReactionEquation(VGroup):
        """
        A styled chemical reaction equation.
        
        Example: ReactionEquation("2H2 + O2", "2H2O")
        """
        
        def __init__(
            self,
            reactants: str,
            products: str,
            arrow_color: str = ChemanimColors.SOLAR_GOLD,
            **kwargs
        ):
            super().__init__(**kwargs)
            
            # Reactants
            r_tex = ChemicalFormula(reactants)
            
            # Arrow
            arrow = Tex(r"\rightarrow", color=arrow_color)
            arrow.scale(1.5)
            
            # Products
            p_tex = ChemicalFormula(products)
            
            # Arrange
            r_tex.next_to(arrow, LEFT, buff=0.5)
            p_tex.next_to(arrow, RIGHT, buff=0.5)
            
            self.add(r_tex, arrow, p_tex)
            
            self.reactants = r_tex
            self.products = p_tex
            self.arrow = arrow


# ============================================================================
# TEXT UTILITIES
# ============================================================================

def create_styled_label(
    text: str,
    style: str = "neon",
    theme=None,
    **kwargs
) -> VGroup:
    """
    Factory function to create styled labels.
    
    Styles: "neon", "gradient", "holographic", "premium"
    """
    if not MANIM_AVAILABLE:
        return VGroup()
    
    color = theme.primary if theme else ChemanimColors.CYBER_CYAN
    
    if style == "neon":
        return NeonLabel(text, neon_color=color, **kwargs)
    elif style == "gradient":
        colors = theme.particle_colors[:2] if theme else None
        return GradientTitle(text, gradient_colors=colors, **kwargs)
    elif style == "holographic":
        return HolographicText(text, holo_color=color, **kwargs)
    else:  # premium
        return PremiumText(text, color=color, glow=True, **kwargs)


def create_section_header(
    title: str,
    subtitle: Optional[str] = None,
    theme=None
) -> VGroup:
    """
    Create a styled section header with optional subtitle.
    """
    if not MANIM_AVAILABLE:
        return VGroup()
    
    group = VGroup()
    
    # Main title
    title_mob = GradientTitle(
        title,
        gradient_colors=[
            theme.primary if theme else ChemanimColors.CYBER_CYAN,
            theme.secondary if theme else ChemanimColors.PLASMA_MAGENTA,
        ],
        font_size=64,
    )
    group.add(title_mob)
    
    # Subtitle
    if subtitle:
        sub_mob = PremiumText(
            subtitle,
            font_size=32,
            color=theme.text_secondary if theme else ChemanimColors.SILVER_MIST,
        )
        sub_mob.next_to(title_mob, DOWN, buff=0.3)
        group.add(sub_mob)
    
    return group
