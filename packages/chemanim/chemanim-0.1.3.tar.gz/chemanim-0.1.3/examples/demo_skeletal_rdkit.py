from manimlib import *
from chemanim import ChemObject

class SkeletalRDKitGallery(Scene):
    def construct(self):
        title = Text("RDKit -> Skeletal", font_size=36).to_edge(UP)
        self.play(Write(title))

        smiles_list = [
            ("Benzene", "c1ccccc1"),
            ("Aspirin", "CC(=O)OC1=CC=CC=C1C(=O)O"),
            ("Ethanol", "CCO"),
            ("Propyne", "CC#C"),
        ]

        rendered = []
        for label, smi in smiles_list:
            try:
                mol = ChemObject.from_smiles_rdkit(smi, skeletal=True, bond_length=1.0)
                rendered.append((label, mol))
            except Exception as e:
                rendered.append((label, Text(f"Failed: {label}", font_size=18, color=RED)))

        cols = 2
        spacing_x, spacing_y = 5.5, 3.5
        for idx, (label, mob) in enumerate(rendered):
            row = idx // cols
            col = idx % cols
            pos = LEFT * spacing_x + RIGHT * spacing_x * col + DOWN * spacing_y * row + DOWN * 0.8
            mob.move_to(pos)
            label_text = Text(label, font_size=18).next_to(mob, DOWN, buff=0.25)
            self.play(Create(mob), Write(label_text))

        self.wait(3)
