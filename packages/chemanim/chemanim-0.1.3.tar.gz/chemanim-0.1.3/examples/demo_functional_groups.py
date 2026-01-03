from manimlib import *

from chemanim.chem_object import ChemObject
from chemanim.rdkit_adapter import (
    detect_functional_groups,
    functional_group_palette,
    molecule_data_from_smiles,
)


class FunctionalGroupsDemo(Scene):
    """Showcase common functional groups with RDKit detection overlays."""

    def construct(self):
        title = Text("Functional Group Gallery", font_size=36).to_edge(UP)
        palette = functional_group_palette()

        examples = [
            ("CCO", "Alcohol (ethanol)"),
            ("O=C(O)CCl", "Acyl halide"),
            ("CC(=O)OCC", "Ester"),
            ("c1ccc(cc1)[N+](=O)[O-]", "Nitrobenzene"),
            ("CCN", "Amine"),
            ("CCC#N", "Nitrile"),
        ]

        cards = VGroup()
        for smiles, subtitle in examples:
            data = molecule_data_from_smiles(smiles, add_h=False)
            matches = detect_functional_groups(smiles)

            mol = ChemObject(
                data,
                skeletal=True,
                use_external_coords=True,
                skeletal_carbon_marker_radius=0.06,
                skeletal_carbon_marker_color=GREY_C,
                font_size=28,
                bond_stroke=4,
            )
            mol.scale(0.9)
            mol.add_functional_group_highlights(
                matches,
                palette=palette,
                label_font_size=20,
                fill_opacity=0.12,
                stroke_width=3,
                buff=0.6,
                show_labels=True,
            )

            caption = Text(subtitle, font_size=22)
            caption.next_to(mol, DOWN, buff=0.25)
            card = VGroup(mol, caption)
            cards.add(card)

        cards.arrange_in_grid(rows=2, cols=3, buff=1.2, cell_alignment=ORIGIN)

        self.play(Write(title))
        self.play(FadeIn(cards, shift=UP * 0.2, lag_ratio=0.1))
        self.wait(3)
