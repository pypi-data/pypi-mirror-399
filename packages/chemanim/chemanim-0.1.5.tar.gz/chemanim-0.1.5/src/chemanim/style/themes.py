"""
Chemanim Style - Theme System
=============================

Complete theme configurations for consistent premium styling.
Each theme includes colors, effects, typography, and animation settings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .colors import ChemanimColors, GradientPalette


@dataclass
class ThemeConfig:
    """Complete theme configuration."""
    
    name: str
    
    # Background
    background_color: str
    background_gradient: Optional[List[str]] = None
    
    # Primary colors
    primary: str = ""
    secondary: str = ""
    accent: str = ""
    
    # Text colors
    text_primary: str = ""
    text_secondary: str = ""
    text_accent: str = ""
    
    # UI Element colors
    panel_bg: str = ""
    panel_border: str = ""
    
    # Effect settings
    glow_color: str = ""
    glow_intensity: float = 0.5
    glow_radius: float = 10
    
    # Particle settings
    particle_colors: List[str] = field(default_factory=list)
    particle_count: int = 50
    
    # Animation settings
    default_animation_speed: float = 1.0
    easing_style: str = "smooth"  # smooth, bounce, elastic, linear
    
    # Glassmorphism settings
    glass_blur: float = 10
    glass_opacity: float = 0.2
    glass_border_opacity: float = 0.3
    
    # Typography
    heading_font: str = "Inter"
    body_font: str = "Inter" 
    mono_font: str = "JetBrains Mono"
    
    # Special effect toggles
    enable_glow: bool = True
    enable_particles: bool = True
    enable_glassmorphism: bool = True


# ============================================================================
# PRE-DEFINED THEMES - Your Signature Styles
# ============================================================================

CYBER_NEON = ThemeConfig(
    name="Cyber Neon",
    background_color=ChemanimColors.DEEP_SPACE,
    background_gradient=["#0A0A0F", "#1A0A2E", "#0A0A0F"],
    
    primary=ChemanimColors.CYBER_CYAN,
    secondary=ChemanimColors.PLASMA_MAGENTA,
    accent=ChemanimColors.NEON_GREEN,
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary=ChemanimColors.SILVER_MIST,
    text_accent=ChemanimColors.CYBER_CYAN,
    
    panel_bg=ChemanimColors.CARBON_GREY + "40",
    panel_border=ChemanimColors.CYBER_CYAN + "80",
    
    glow_color=ChemanimColors.CYBER_CYAN,
    glow_intensity=0.7,
    glow_radius=15,
    
    particle_colors=GradientPalette.QUANTUM_SHIFT,
    particle_count=100,
    
    easing_style="smooth",
    
    glass_blur=15,
    glass_opacity=0.15,
    glass_border_opacity=0.5,
)


AURORA_GLOW = ThemeConfig(
    name="Aurora Glow",
    background_color=ChemanimColors.MIDNIGHT_BLUE,
    background_gradient=["#0D1B2A", "#1B2838", "#0D1B2A"],
    
    primary=ChemanimColors.AURORA_TEAL,
    secondary="#00FFA3",
    accent="#FFE500",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary=ChemanimColors.ICE_BLUE,
    text_accent="#00FFA3",
    
    panel_bg="#0F2840" + "50",
    panel_border="#00FFA3" + "60",
    
    glow_color="#00FFA3",
    glow_intensity=0.6,
    glow_radius=12,
    
    particle_colors=GradientPalette.AURORA_BOREALIS,
    particle_count=80,
    
    easing_style="smooth",
    
    glass_blur=12,
    glass_opacity=0.2,
    glass_border_opacity=0.4,
)


QUANTUM_FROST = ThemeConfig(
    name="Quantum Frost",
    background_color="#0A1628",
    background_gradient=["#0A1628", "#1A2A48", "#0A1628"],
    
    primary="#60A5FA",
    secondary="#A78BFA",
    accent="#F472B6",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#94A3B8",
    text_accent="#60A5FA",
    
    panel_bg="#1E3A5F" + "40",
    panel_border="#60A5FA" + "50",
    
    glow_color="#60A5FA",
    glow_intensity=0.5,
    glow_radius=10,
    
    particle_colors=["#60A5FA", "#A78BFA", "#F472B6", "#FFFFFF"],
    particle_count=60,
    
    easing_style="smooth",
    
    glass_blur=20,
    glass_opacity=0.15,
    glass_border_opacity=0.3,
)


SOLAR_FLARE = ThemeConfig(
    name="Solar Flare",
    background_color="#1A0A00",
    background_gradient=["#1A0A00", "#2A1500", "#1A0A00"],
    
    primary=ChemanimColors.SOLAR_GOLD,
    secondary="#FF6B00",
    accent="#FF4500",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#FFE4B5",
    text_accent=ChemanimColors.SOLAR_GOLD,
    
    panel_bg="#3A2000" + "50",
    panel_border=ChemanimColors.SOLAR_GOLD + "60",
    
    glow_color=ChemanimColors.SOLAR_GOLD,
    glow_intensity=0.8,
    glow_radius=20,
    
    particle_colors=GradientPalette.SOLAR_FLARE,
    particle_count=120,
    
    easing_style="bounce",
    
    glass_blur=8,
    glass_opacity=0.25,
    glass_border_opacity=0.5,
)


DEEP_OCEAN = ThemeConfig(
    name="Deep Ocean",
    background_color="#001220",
    background_gradient=["#001220", "#002040", "#001220"],
    
    primary="#00B4D8",
    secondary="#0077B6",
    accent="#90E0EF",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#CAF0F8",
    text_accent="#00B4D8",
    
    panel_bg="#003050" + "40",
    panel_border="#00B4D8" + "50",
    
    glow_color="#00B4D8",
    glow_intensity=0.5,
    glow_radius=12,
    
    particle_colors=GradientPalette.DEEP_OCEAN,
    particle_count=70,
    
    easing_style="smooth",
    
    glass_blur=15,
    glass_opacity=0.2,
    glass_border_opacity=0.35,
)


COSMIC_DUST = ThemeConfig(
    name="Cosmic Dust",
    background_color="#0A0015",
    background_gradient=["#0A0015", "#1A0030", "#0A0015"],
    
    primary="#FF2E63",
    secondary="#7B2D8E",
    accent="#FFB800",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#E0C0FF",
    text_accent="#FF2E63",
    
    panel_bg="#2A0040" + "40",
    panel_border="#FF2E63" + "50",
    
    glow_color="#FF2E63",
    glow_intensity=0.6,
    glow_radius=15,
    
    particle_colors=GradientPalette.COSMIC_DUST,
    particle_count=90,
    
    easing_style="elastic",
    
    glass_blur=12,
    glass_opacity=0.18,
    glass_border_opacity=0.4,
)


EMERALD_MATRIX = ThemeConfig(
    name="Emerald Matrix",
    background_color="#001A0A",
    background_gradient=["#001A0A", "#003015", "#001A0A"],
    
    primary="#38B000",
    secondary="#70E000",
    accent="#CCFF33",
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#A0FFA0",
    text_accent="#70E000",
    
    panel_bg="#003020" + "40",
    panel_border="#38B000" + "60",
    
    glow_color="#38B000",
    glow_intensity=0.6,
    glow_radius=12,
    
    particle_colors=GradientPalette.EMERALD_MATRIX,
    particle_count=80,
    
    easing_style="smooth",
    
    glass_blur=10,
    glass_opacity=0.2,
    glass_border_opacity=0.4,
)


ROYAL_VELVET = ThemeConfig(
    name="Royal Velvet",
    background_color="#0D001A",
    background_gradient=["#0D001A", "#1A0033", "#0D001A"],
    
    primary="#8B008B",
    secondary="#DA70D6",
    accent=ChemanimColors.SOLAR_GOLD,
    
    text_primary=ChemanimColors.FROST_WHITE,
    text_secondary="#E0B0FF",
    text_accent="#DA70D6",
    
    panel_bg="#2A0050" + "40",
    panel_border="#8B008B" + "60",
    
    glow_color="#DA70D6",
    glow_intensity=0.5,
    glow_radius=12,
    
    particle_colors=GradientPalette.ROYAL_VELVET,
    particle_count=60,
    
    easing_style="smooth",
    
    glass_blur=15,
    glass_opacity=0.2,
    glass_border_opacity=0.35,
)


# ============================================================================
# THEME REGISTRY
# ============================================================================

THEMES = {
    "cyber_neon": CYBER_NEON,
    "aurora_glow": AURORA_GLOW,
    "quantum_frost": QUANTUM_FROST,
    "solar_flare": SOLAR_FLARE,
    "deep_ocean": DEEP_OCEAN,
    "cosmic_dust": COSMIC_DUST,
    "emerald_matrix": EMERALD_MATRIX,
    "royal_velvet": ROYAL_VELVET,
}


def get_theme(name: str) -> ThemeConfig:
    """Get a theme by name (case-insensitive)."""
    key = name.lower().replace(" ", "_")
    if key not in THEMES:
        raise ValueError(f"Theme '{name}' not found. Available: {list(THEMES.keys())}")
    return THEMES[key]


def list_themes() -> List[str]:
    """List all available theme names."""
    return list(THEMES.keys())
