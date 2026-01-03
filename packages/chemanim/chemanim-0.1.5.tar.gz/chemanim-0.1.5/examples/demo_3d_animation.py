from manim import *
from chemanim.chem_object_3d import ChemObject3D

class MoleculeSpinSlide(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=2.6)

        mol = ChemObject3D.from_smiles_rdkit(
            "CCO",
            add_h=True,
            coord_scale=1.0,
            atom_radius_scale=0.3,
            show_labels=True,
        ).enable_dynamic_bonds()
        mol.enable_label_billboarding(self.camera)
        mol.move_to(ORIGIN)
        self.add(mol)

        self.play(Rotate(mol, angle=PI / 2, axis=UP), run_time=2)
        self.play(Rotate(mol, angle=PI / 2, axis=RIGHT), run_time=2)
        self.play(mol.animate.shift(LEFT * 2), run_time=1.5)
        self.play(mol.animate.shift(RIGHT * 4), run_time=1.5)
        self.play(mol.animate.shift(LEFT * 2), run_time=1.0)
        self.wait(1)

# Run:
# D:/Law/Chemanim/env311/Scripts/python.exe -m manim -pql examples/demo_3d_animation.py MoleculeSpinSlide
