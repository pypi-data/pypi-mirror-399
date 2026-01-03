from manimlib import *

from chemanim.chem_object import ChemObject
from chemanim.rdkit_adapter import molecule_data_from_smiles


class LonePairShowcase(Scene):
    def construct(self):
        examples = [
            {"smiles": "O", "label": "Water (2 lone pairs)", "pairs": {0: 2}, "add_h": True},
            {"smiles": "N", "label": "Ammonia (1 lone pair)", "pairs": {0: 1}, "add_h": True},
            {"smiles": "[Cl-]", "label": "Chloride (3 lone pairs)", "pairs": {0: 3}, "add_h": False},
        ]

        cards = VGroup()
        for item in examples:
            data = molecule_data_from_smiles(item["smiles"], add_h=item.get("add_h", False))
            mol = ChemObject(
                data,
                skeletal=False,
                use_external_coords=True,
                bond_length=1.1,
                bond_stroke=4,
                font_size=32,
            )
            # Attach lone pairs (indices follow RDKit atom order; heavy atom is index 0 here)
            mol.add_lone_pairs(item["pairs"], radius=0.06, distance=mol.bond_length * 0.38, color=YELLOW)
            mol.enable_dynamic_bonds()

            label = Text(item["label"], font_size=24)
            label.next_to(mol, DOWN, buff=0.3)
            card = VGroup(mol, label)
            cards.add(card)

        cards.arrange_in_grid(rows=1, cols=len(cards), buff=1.5, cell_alignment=ORIGIN)
        self.play(FadeIn(cards, lag_ratio=0.1, shift=UP * 0.2))
        self.wait(3)


# Run with:
# python -m manim -pql examples/demo_lone_pairs.py LonePairShowcase
