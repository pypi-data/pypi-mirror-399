from manim import *
from chemanim.chem_object_3d import ChemObject3D

STYLES = [
    ("ball_and_stick", "Ball & Stick"),
    ("stick", "Sticks"),
    ("wire", "Wire"),
    ("space_fill", "Space Filling"),
]

class PubChemStyleGallery(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-35 * DEGREES, zoom=2.2)

        molecules = []
        for style, label in STYLES:
            mol = ChemObject3D.from_pubchem(
                "ethanol",  # small, fast to fetch/render
                prefer_3d=True,
                coord_scale=1.0,
                atom_radius_scale=0.28,
                show_labels=False,
                render_style=style,
            ).enable_dynamic_bonds()
            mol.enable_label_billboarding(self.camera)
            molecules.append((mol, label))

        # Arrange in a 2x2 grid
        positions = [UP + LEFT, UP + RIGHT, DOWN + LEFT, DOWN + RIGHT]
        for (mol, label), pos in zip(molecules, positions):
            mol.scale(0.9).move_to(pos)
            caption = Text(label, font_size=28).next_to(mol, DOWN, buff=0.3)
            self.add(mol, caption)

        # A gentle collective rotation to show depth
        group = VGroup(*[m for m, _ in molecules])
        self.play(Rotate(group, angle=PI / 3, axis=OUT), run_time=3)
        self.play(Rotate(group, angle=-PI / 3, axis=UP), run_time=3)
        self.wait(1)

# Run:
# D:/Law/Chemanim/env311/Scripts/python.exe -m manim -pql examples/demo_pubchem_styles.py PubChemStyleGallery
