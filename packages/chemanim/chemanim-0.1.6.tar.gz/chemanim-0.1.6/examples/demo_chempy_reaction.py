from manimlib import *
from chemanim.chempy_adapter import build_reaction_chemobjects

class ChemPyReaction(Scene):
    def construct(self):
        title = Text("ChemPy Reaction (RDKit layouts)", font_size=32).to_edge(UP)
        self.play(Write(title))

        # Example: combustion of methane
        equation = "CH4 + 2 O2 -> CO2 + 2 H2O"
        species_to_smiles = {
            "CH4": "C",
            "O2": "O=O",
            "CO2": "O=C=O",
            "H2O": "O",
        }

        reactants, products = build_reaction_chemobjects(
            equation,
            species_to_smiles,
            chemobject_kwargs={"skeletal": True, "bond_length": 1.0},
            add_h=True,
        )

        left_group = VGroup(*[mob for _, mob in reactants]).arrange(RIGHT, buff=1.2)
        right_group = VGroup(*[mob for _, mob in products]).arrange(RIGHT, buff=1.2)

        arrow = Tex("$\\Rightarrow$", font_size=40)
        full = VGroup(left_group, arrow, right_group).arrange(RIGHT, buff=1.5).shift(DOWN * 0.5)

        self.play(Create(left_group), Write(arrow), Create(right_group))
        self.wait(2)
