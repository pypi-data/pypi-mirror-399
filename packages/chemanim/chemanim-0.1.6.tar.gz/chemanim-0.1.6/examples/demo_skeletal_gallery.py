from manimlib import *
from chemanim import ChemObject


def single_molecule_scene(label: str, identifier: str, bond_length: float = 1.0):
    class Single(Scene):
        def construct(self_inner):
            title = Text(label, font_size=32).to_edge(UP)
            self_inner.play(Write(title))
            try:
                mol = ChemObject.from_pubchem(
                    identifier,
                    bond_length=bond_length,
                    zigzag_chain=True,
                    skeletal=True,
                )
                mol.move_to(ORIGIN)
                self_inner.play(Create(mol))
            except Exception as e:
                err = Text(f"Failed: {label}", font_size=20, color=RED)
                self_inner.add(err)
            self_inner.wait(2)

    Single.__name__ = label.replace(" ", "").replace("(", "").replace(")", "")
    return Single


HexaneSkeletal = single_molecule_scene("Hexane (alkane)", "Hexane", bond_length=1.1)
CyclohexaneSkeletal = single_molecule_scene("Cyclohexane (alkane)", "Cyclohexane", bond_length=1.1)
EtheneSkeletal = single_molecule_scene("Ethene (alkene)", "Ethene", bond_length=1.0)
PropeneSkeletal = single_molecule_scene("Propene (alkene)", "Propene", bond_length=1.0)
EthyneSkeletal = single_molecule_scene("Ethyne (alkyne)", "Acetylene", bond_length=1.0)
AcetoneSkeletal = single_molecule_scene("Acetone (ketone)", "Acetone", bond_length=1.0)
AceticAcidSkeletal = single_molecule_scene("Acetic acid (carboxy)", "Acetic acid", bond_length=1.0)
EthanolSkeletal = single_molecule_scene("Ethanol (alcohol)", "Ethanol", bond_length=1.0)
AnilineSkeletal = single_molecule_scene("Aniline (amine)", "Aniline", bond_length=1.0)
