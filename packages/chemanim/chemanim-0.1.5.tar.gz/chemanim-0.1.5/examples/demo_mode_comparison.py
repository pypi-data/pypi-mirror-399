from manimlib import *
from chemanim import ChemObject

class ModeComparison(Scene):
    def construct(self):
        title = Text("Mode Comparison", font_size=36).to_edge(UP)
        self.play(Write(title))

        cases = [
            ("Hexane", "CCCCCC", 1.0),
            ("Ethanol", "CCO", 1.0),
            ("Propyne", "CC#C", 1.0),
        ]

        y_start = 2.5
        y_step = 3.0

        for row, (label, smiles, blen) in enumerate(cases):
            y = y_start - row * y_step

            rdkit = ChemObject.from_smiles_rdkit(smiles, skeletal=True, bond_length=blen)
            rdkit.move_to(LEFT * 5 + UP * (y - y_start))
            rdkit_label = Text(f"{label} (RDKit layout)", font_size=18).next_to(rdkit, DOWN, buff=0.25)

            straight = ChemObject.from_smiles_rdkit(
                smiles,
                skeletal=False,  # show all atoms (C/H) like the earlier full-label mode
                bond_length=blen,
                straight_chain=True,
                use_external_coords=False,  # use our straight layout instead of RDKit coords
                add_h=True,  # ensure hydrogens are included from RDKit
            )
            straight.move_to(ORIGIN + UP * (y - y_start))
            straight_label = Text(f"{label} (straight, full labels)", font_size=18).next_to(straight, DOWN, buff=0.25)

            zigzag = ChemObject.from_smiles_rdkit(
                smiles,
                skeletal=True,
                bond_length=blen,
                zigzag_chain=True,
                use_external_coords=True,  # let zigzag use RDKit coords but still labeled as zigzag mode
            )
            zigzag.move_to(RIGHT * 5 + UP * (y - y_start))
            zigzag_label = Text(f"{label} (zigzag)", font_size=18).next_to(zigzag, DOWN, buff=0.25)

            self.play(Create(rdkit), Write(rdkit_label))
            self.play(Create(straight), Write(straight_label))
            self.play(Create(zigzag), Write(zigzag_label))

        self.wait(3)
