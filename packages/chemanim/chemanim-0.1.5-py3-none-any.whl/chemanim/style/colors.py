"""
Chemanim Style - Premium Color System
=====================================

A sophisticated color system featuring:
- HSL-based color harmonies
- Curated gradient palettes  
- Element-specific themed colors
- Accessibility-friendly contrasts

Differentiating from 3Blue1Brown's blue/brown/grey palette with
vibrant, modern, premium aesthetics.
"""

import colorsys
from typing import List, Tuple, Optional

# ============================================================================
# CORE SIGNATURE COLORS (Your Distinctive Palette)
# ============================================================================

class ChemanimColors:
    """
    Premium color palette for Chemanim - distinctively different from 3B1B.
    
    3Blue1Brown uses: blues, browns, greys, dark backgrounds
    We use: vibrant cyans, magentas, golds, with neon accents
    """
    
    # ----- PRIMARY SIGNATURE COLORS -----
    # These are YOUR brand colors - distinctive and premium
    
    # Cyber Cyan - Electric and futuristic
    CYBER_CYAN = "#00FFFF"
    CYBER_CYAN_DARK = "#00B8B8"
    CYBER_CYAN_LIGHT = "#7FFFFF"
    CYBER_CYAN_GLOW = "#00FFFF40"
    
    # Plasma Magenta - Energetic and bold
    PLASMA_MAGENTA = "#FF00FF"
    PLASMA_MAGENTA_DARK = "#B800B8"
    PLASMA_MAGENTA_LIGHT = "#FF7FFF"
    PLASMA_MAGENTA_GLOW = "#FF00FF40"
    
    # Solar Gold - Premium and luxurious  
    SOLAR_GOLD = "#FFD700"
    SOLAR_GOLD_DARK = "#B89B00"
    SOLAR_GOLD_LIGHT = "#FFE87F"
    SOLAR_GOLD_GLOW = "#FFD70040"
    
    # Electric Violet - Mysterious and deep
    ELECTRIC_VIOLET = "#8A2BE2"
    ELECTRIC_VIOLET_DARK = "#5B1D94"
    ELECTRIC_VIOLET_LIGHT = "#B57FE8"
    ELECTRIC_VIOLET_GLOW = "#8A2BE240"
    
    # Neon Green - Scientific and vibrant
    NEON_GREEN = "#39FF14"
    NEON_GREEN_DARK = "#28B30E"
    NEON_GREEN_LIGHT = "#8CFF75"
    NEON_GREEN_GLOW = "#39FF1440"
    
    # Aurora Teal - Elegant and calming
    AURORA_TEAL = "#20B2AA"
    AURORA_TEAL_DARK = "#167A75"
    AURORA_TEAL_LIGHT = "#7DD4D0"
    AURORA_TEAL_GLOW = "#20B2AA40"
    
    # ----- BACKGROUND COLORS -----
    # Premium dark backgrounds with subtle color tints
    
    DEEP_SPACE = "#0A0A0F"      # Near black with blue tint
    MIDNIGHT_BLUE = "#0D1B2A"   # Rich dark blue
    OBSIDIAN = "#0F0F1A"        # Purple-tinted black  
    VOID_BLACK = "#050508"      # Ultra dark
    CARBON_GREY = "#1A1A2E"     # Sophisticated grey-purple
    
    # ----- ACCENT COLORS -----
    
    FROST_WHITE = "#F0F8FF"     # Soft white with blue tint
    ICE_BLUE = "#E0F7FA"        # Cool light blue
    PEARL = "#FAFAFF"           # Premium off-white
    SILVER_MIST = "#C0C0D0"     # Elegant grey
    
    # ----- ELEMENT COLORS (Enhanced from periodic table) -----
    # More vibrant versions for animations
    
    HYDROGEN = "#FFFFFF"
    CARBON = "#404040"
    NITROGEN = "#3050F8"
    OXYGEN = "#FF2A2A"
    SULFUR = "#FFD800"
    PHOSPHORUS = "#FF8000"
    CHLORINE = "#1FF01F"
    FLUORINE = "#90E050"
    BROMINE = "#A62929"
    IODINE = "#940094"
    
    # Metal colors with metallic sheen effect values
    IRON = "#E06633"
    COPPER = "#C88033"
    GOLD_METAL = "#FFD123"
    SILVER_METAL = "#C0C0C0"
    PLATINUM = "#D0D0E0"
    
    # ----- SEMANTIC COLORS -----
    
    SUCCESS = "#4ADE80"         # Green success
    WARNING = "#FACC15"         # Yellow warning
    ERROR = "#F87171"           # Red error
    INFO = "#60A5FA"            # Blue info
    
    # ----- GRADIENT BUILDING BLOCKS -----
    
    @classmethod
    def create_gradient(cls, start_color: str, end_color: str, steps: int = 5) -> List[str]:
        """Generate smooth gradient between two hex colors."""
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            h = hex_color.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        start_rgb = hex_to_rgb(start_color)
        end_rgb = hex_to_rgb(end_color)
        
        gradient = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            gradient.append(rgb_to_hex((r, g, b)))
        
        return gradient
    
    @classmethod
    def create_harmonious_palette(cls, base_hue: float, saturation: float = 0.8, 
                                   lightness: float = 0.5) -> dict:
        """
        Create a harmonious color palette from a base hue (0-1).
        Returns complementary, triadic, and analogous colors.
        """
        def hsl_to_hex(h: float, s: float, l: float) -> str:
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
        
        return {
            'primary': hsl_to_hex(base_hue, saturation, lightness),
            'complementary': hsl_to_hex((base_hue + 0.5) % 1, saturation, lightness),
            'triadic_1': hsl_to_hex((base_hue + 0.333) % 1, saturation, lightness),
            'triadic_2': hsl_to_hex((base_hue + 0.666) % 1, saturation, lightness),
            'analogous_1': hsl_to_hex((base_hue + 0.083) % 1, saturation, lightness),
            'analogous_2': hsl_to_hex((base_hue - 0.083) % 1, saturation, lightness),
            'light': hsl_to_hex(base_hue, saturation * 0.7, lightness + 0.2),
            'dark': hsl_to_hex(base_hue, saturation * 0.9, lightness - 0.2),
            'glow': hsl_to_hex(base_hue, saturation, lightness) + '60',
        }


# ============================================================================
# GRADIENT PALETTES
# ============================================================================

class GradientPalette:
    """Pre-defined premium gradient color schemes."""
    
    # Signature gradients for Chemanim
    CYBER_SUNSET = ["#FF6B6B", "#FF8E53", "#FFD93D", "#6BCB77"]
    AURORA_BOREALIS = ["#00D9FF", "#00FFA3", "#FFE500", "#FF00D4"]
    QUANTUM_SHIFT = ["#8A2BE2", "#00FFFF", "#FF00FF", "#39FF14"]
    DEEP_OCEAN = ["#0077B6", "#00B4D8", "#90E0EF", "#CAF0F8"]
    SOLAR_FLARE = ["#FF4500", "#FF6B00", "#FFD700", "#FFF8DC"]
    COSMIC_DUST = ["#2C1654", "#7B2D8E", "#FF2E63", "#FFB800"]
    EMERALD_MATRIX = ["#004B23", "#006400", "#38B000", "#70E000", "#CCFF33"]
    ROYAL_VELVET = ["#1A0033", "#4B0082", "#8B008B", "#DA70D6"]
    
    # Chemistry-specific gradients
    REACTION_ENERGY = ["#3498db", "#9b59b6", "#e74c3c", "#f39c12"]  # Cold to hot
    ELECTRONEGATIVITY = ["#27ae60", "#f1c40f", "#e74c3c"]  # Low to high
    PH_SCALE = ["#e74c3c", "#f39c12", "#f1c40f", "#27ae60", "#2980b9", "#8e44ad"]
    
    # Biological gradients
    DNA_HELIX = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#DDA0DD"]
    PROTEIN_FOLD = ["#FF69B4", "#FFD700", "#32CD32", "#4169E1"]
    LIPID_BILAYER = ["#20B2AA", "#FF8C00", "#20B2AA"]
    
    @classmethod
    def get_interpolated(cls, palette_name: str, position: float) -> str:
        """
        Get interpolated color from a gradient at a specific position (0-1).
        """
        palette = getattr(cls, palette_name, cls.CYBER_SUNSET)
        n = len(palette)
        
        if position <= 0:
            return palette[0]
        if position >= 1:
            return palette[-1]
        
        scaled = position * (n - 1)
        idx = int(scaled)
        blend = scaled - idx
        
        # Blend between two adjacent colors
        c1 = palette[idx]
        c2 = palette[min(idx + 1, n - 1)]
        
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        rgb1 = hex_to_rgb(c1)
        rgb2 = hex_to_rgb(c2)
        
        blended = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * blend) for i in range(3))
        return rgb_to_hex(blended)


# ============================================================================
# COLOR UTILITIES
# ============================================================================

def with_alpha(hex_color: str, alpha: float) -> str:
    """Add alpha transparency to a hex color. Alpha: 0-1."""
    alpha_hex = format(int(alpha * 255), '02x')
    return hex_color + alpha_hex


def lighten(hex_color: str, amount: float = 0.2) -> str:
    """Lighten a hex color by a given amount (0-1)."""
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    
    # Convert to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = min(1, l + amount)
    
    # Convert back
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))


def darken(hex_color: str, amount: float = 0.2) -> str:
    """Darken a hex color by a given amount (0-1)."""
    return lighten(hex_color, -amount)


def saturate(hex_color: str, amount: float = 0.2) -> str:
    """Increase saturation of a hex color."""
    h = hex_color.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    
    h, l, s = colorsys.rgb_to_hls(*rgb)
    s = min(1, s + amount)
    
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))


def get_contrast_color(hex_color: str) -> str:
    """Get white or black text color for best contrast."""
    h = hex_color.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    
    # Calculate relative luminance
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    
    return ChemanimColors.FROST_WHITE if luminance < 0.5 else ChemanimColors.DEEP_SPACE
