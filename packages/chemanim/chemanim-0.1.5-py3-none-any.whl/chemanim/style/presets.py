"""
Chemanim Style - Presets
=========================

Ready-to-use styled molecules, reactions, and other preset configurations.
These apply the Chemanim premium styling to common chemistry visualizations.
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    class VGroup:
        def __init__(self, *args, **kwargs): pass
        def add(self, *mobject): return self
        def set_stroke(self, *args, **kwargs): return self

from typing import Optional, Dict, Any
from .colors import ChemanimColors, GradientPalette
from .themes import ThemeConfig, CYBER_NEON


# ============================================================================
# STYLED MOLECULE PRESETS
# ============================================================================

def apply_premium_style(
    mobject,
    theme: ThemeConfig = CYBER_NEON,
    glow: bool = True,
    intensity: float = 0.5
):
    """
    Apply premium Chemanim styling to any mobject.
    
    This adds glow effects, themed colors, and premium polish.
    """
    if not MANIM_AVAILABLE:
        return mobject
    
    if glow:
        mobject.set_stroke(theme.glow_color, width=4, opacity=intensity * 0.5)
    
    return mobject


def create_styled_molecule(
    identifier: str,
    theme: ThemeConfig = CYBER_NEON,
    render_style: str = "ball_and_stick",
    glow: bool = True
):
    """
    Create a molecule with premium Chemanim styling applied.
    
    Args:
        identifier: PubChem identifier (name or CID)
        theme: Theme configuration to apply
        render_style: "ball_and_stick", "space_filling", "wireframe"
        glow: Whether to add glow effects
    
    Returns:
        Styled molecule Mobject
    """
    from ..core import Molecule
    
    molecule = Molecule.from_pubchem(identifier)
    
    if glow:
        apply_premium_style(molecule, theme, glow=True)
    
    return molecule


def create_styled_molecule_3d(
    identifier: str,
    theme: ThemeConfig = CYBER_NEON,
    render_style: str = "ball_and_stick",
    glow: bool = True
):
    """
    Create a 3D molecule with premium styling.
    """
    from ..chem_object_3d import ChemObject3D
    
    molecule = ChemObject3D.from_name(identifier, render_style=render_style)
    
    if glow:
        apply_premium_style(molecule, theme, glow=True, intensity=0.3)
    
    return molecule


# ============================================================================
# STYLED REACTION PRESETS
# ============================================================================

def create_styled_reaction(
    reactants: list,
    products: list,
    theme: ThemeConfig = CYBER_NEON,
    with_energy_effect: bool = True
):
    """
    Create a chemical reaction with premium styling.
    
    Args:
        reactants: List of reactant identifiers
        products: List of product identifiers
        theme: Theme configuration
        with_energy_effect: Add energy flow visualization
    
    Returns:
        Styled ChemicalReaction object
    """
    from ..reaction import ChemicalReaction
    
    reaction = ChemicalReaction(
        reactants_ids=reactants,
        products_ids=products
    )
    
    apply_premium_style(reaction, theme)
    
    return reaction


# ============================================================================
# TITLE CARD PRESETS
# ============================================================================

def create_title_card(
    title: str,
    subtitle: Optional[str] = None,
    theme: ThemeConfig = CYBER_NEON
):
    """
    Create a styled title card with optional subtitle.
    """
    if not MANIM_AVAILABLE:
        return VGroup()
    
    from .typography import GradientTitle, PremiumText
    from .effects import GlassmorphismPanel
    
    group = VGroup()
    
    # Background panel
    panel = GlassmorphismPanel(
        width=10,
        height=3,
        fill_opacity=theme.glass_opacity,
        border_color=theme.primary,
        glow=theme.enable_glow,
        glow_color=theme.glow_color
    )
    group.add(panel)
    
    # Title
    title_text = GradientTitle(
        title,
        gradient_colors=[theme.primary, theme.secondary],
        font_size=64
    )
    group.add(title_text)
    
    # Subtitle
    if subtitle:
        sub_text = PremiumText(
            subtitle,
            color=theme.text_secondary,
            font_size=28
        )
        sub_text.next_to(title_text, DOWN, buff=0.4)
        group.add(sub_text)
    
    return group


def create_info_panel(
    title: str,
    content_lines: list,
    theme: ThemeConfig = CYBER_NEON,
    width: float = 6,
    height: float = 4
):
    """
    Create an information panel with styled text.
    """
    if not MANIM_AVAILABLE:
        return VGroup()
    
    from .typography import PremiumText, NeonLabel
    from .effects import GlassmorphismPanel
    
    group = VGroup()
    
    # Panel background
    panel = GlassmorphismPanel(
        width=width,
        height=height,
        fill_opacity=theme.glass_opacity * 1.2,
        border_color=theme.primary
    )
    group.add(panel)
    
    # Title at top
    title_text = NeonLabel(title, neon_color=theme.primary, font_size=32)
    title_text.move_to(panel.get_top()).shift(DOWN * 0.6)
    group.add(title_text)
    
    # Content lines
    y_offset = -0.3
    for line in content_lines:
        line_text = PremiumText(line, color=theme.text_primary, font_size=24)
        line_text.move_to(panel.get_center()).shift(UP * y_offset)
        y_offset -= 0.4
        group.add(line_text)
    
    return group


# ============================================================================
# PROTEIN STYLING PRESETS
# ============================================================================

def create_styled_protein(
    pdb_id: str,
    theme: ThemeConfig = CYBER_NEON,
    color_scheme: str = "spectrum",
    render_style: str = "cartoon"
):
    """
    Create a protein with premium Chemanim styling.
    
    Args:
        pdb_id: PDB identifier
        theme: Theme configuration
        color_scheme: "spectrum", "chain", "secondary", "element"
        render_style: "cartoon", "ribbon", "ball_and_stick", "surface"
    """
    from ..bio import Protein
    
    # Color scheme mapping to theme
    if color_scheme == "spectrum":
        colors = theme.particle_colors
    elif color_scheme == "themed":
        colors = [theme.primary, theme.secondary, theme.accent]
    else:
        colors = None
    
    protein = Protein.from_pdb_id(pdb_id)
    # Note: Would need to apply custom coloring based on scheme
    
    return protein


# ============================================================================
# ANIMATION SEQUENCE PRESETS
# ============================================================================

class AnimationSequence:
    """
    Pre-built animation sequences for common scenarios.
    """
    
    @staticmethod
    def molecule_intro(scene, molecule, theme: ThemeConfig = CYBER_NEON):
        """
        Standard intro animation for a molecule.
        """
        if not MANIM_AVAILABLE:
            return
        
        from .animations import GlowFadeIn
        from .effects import ParticleField
        
        # Particle burst origin
        particles = ParticleField(
            width=4,
            height=4,
            num_particles=40,
            colors=theme.particle_colors
        )
        particles.move_to(molecule.get_center())
        
        scene.play(
            FadeIn(particles, run_time=0.3),
            GlowFadeIn(molecule, glow_color=theme.glow_color, run_time=1.5)
        )
        scene.play(
            FadeOut(particles, run_time=0.5)
        )
    
    @staticmethod
    def reaction_sequence(scene, reaction, theme: ThemeConfig = CYBER_NEON):
        """
        Full reaction animation with themed effects.
        """
        if not MANIM_AVAILABLE:
            return
        
        from .effects import EnergyOrb
        
        # Energy buildup
        energy = EnergyOrb(
            radius=0.4,
            core_color=theme.accent,
            halo_color=theme.primary
        )
        
        scene.play(
            FadeIn(energy, scale=0.5),
            run_time=0.5
        )
        
        scene.play(
            reaction.animate_reaction(run_time=2)
        )
        
        scene.play(
            FadeOut(energy, scale=2),
            run_time=0.5
        )
    
    @staticmethod
    def zoom_to_atom(scene, atom, zoom_factor: float = 3.0, run_time: float = 2.0):
        """
        Dramatic zoom to focus on a specific atom.
        """
        if not MANIM_AVAILABLE:
            return
        
        target_point = atom.get_center()
        
        scene.play(
            scene.camera.frame.animate.move_to(target_point).scale(1/zoom_factor),
            run_time=run_time,
            rate_func=smooth
        )


# ============================================================================
# ELEMENT COLOR SCHEME PRESETS
# ============================================================================

ELEMENT_COLOR_SCHEMES = {
    "neon": {
        "H": ChemanimColors.FROST_WHITE,
        "C": ChemanimColors.CARBON_GREY,
        "N": ChemanimColors.ELECTRIC_VIOLET,
        "O": "#FF4444",
        "S": ChemanimColors.SOLAR_GOLD,
        "P": "#FF8800",
        "F": ChemanimColors.NEON_GREEN,
        "Cl": "#00FF44",
        "Br": "#AA4400",
        "I": ChemanimColors.PLASMA_MAGENTA,
    },
    "quantum": {
        "H": ChemanimColors.CYBER_CYAN,
        "C": "#8888FF",
        "N": ChemanimColors.PLASMA_MAGENTA,
        "O": "#FF6666",
        "S": ChemanimColors.SOLAR_GOLD,
    },
    "bio": {
        "H": "#FFFFFF",
        "C": "#20B2AA",  # Teal for organic
        "N": "#6A5ACD",  # Slate blue for nitrogen
        "O": "#FF6347",  # Tomato red for oxygen
        "S": "#FFD700",  # Gold for sulfur
        "P": "#FF8C00",  # Dark orange for phosphorus
    }
}


def get_element_color(element: str, scheme: str = "neon") -> str:
    """Get the color for an element from a color scheme."""
    colors = ELEMENT_COLOR_SCHEMES.get(scheme, ELEMENT_COLOR_SCHEMES["neon"])
    return colors.get(element, ChemanimColors.SILVER_MIST)
