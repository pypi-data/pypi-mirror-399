from manim import *

from chemanim.chem_object_3d import ChemObject3D


class Molecule3DDemo(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=2.5)

        ethanol = ChemObject3D.from_smiles_rdkit(
            "CCO",
            add_h=True,
            coord_scale=0.9,
            atom_radius_scale=0.28,
            show_labels=True,
        ).enable_dynamic_bonds()

        ethanol.enable_label_billboarding(self.camera)

        ethanol.move_to(ORIGIN)
        self.add(ethanol)

        self.play(Rotate(ethanol, angle=PI / 2, axis=UP), run_time=2)
        self.play(Rotate(ethanol, angle=PI / 2, axis=RIGHT), run_time=2)
        self.wait(2)


# manim -pql examples/demo_3d_molecule.py Molecule3DDemo
