from manimlib import *
from chemanim.bio import Macromolecule
import os

class BioDemo(Scene):  # ManimGL
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        pdb_path = os.path.join(os.path.dirname(__file__), "simple.pdb")
        mol = Macromolecule(pdb_path)
        
        self.add(mol)
        self.wait(1)
        self.move_camera(theta=-45 * DEGREES, run_time=2)
