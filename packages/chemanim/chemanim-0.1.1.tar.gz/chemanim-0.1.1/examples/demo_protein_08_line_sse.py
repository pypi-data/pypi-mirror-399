"""ManimGL Demo: Protein Ball and Stick
"""
from manimlib import *
from chemanim import Protein
import os

class ProteinLineSSEDemo(Scene):
    def construct(self):
        # Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=10 * DEGREES, phi=60 * DEGREES)
        
        # Title
        title = Text("Protein Line (SSE Colored)", font_size=36).to_edge(UP)
        subtitle = Text("Pink: Helix, Gold: Sheet, Grey: Coil", font_size=24, color=GREY).next_to(title, DOWN)
        title.fix_in_frame()
        subtitle.fix_in_frame()
        self.add(title, subtitle)
        
        # Path setup
        pdb_path = "pdb1crn.ent"
        if not os.path.exists(pdb_path):
             pdb_path = os.path.join("examples", "simple.pdb")

        # Load
        print("Loading Protein Line SSE...")
        mol = Protein(pdb_path, render_style="line_sse", include_hydrogens=False, show_heteroatoms=True)
        mol.scale(1.5)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Animate
        self.play(Rotate(mol, angle=2*PI, axis=UP), run_time=10)
