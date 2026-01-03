"""ManimGL Demo: Protein Trace (Backbone Tube)
"""
from manimlib import *
from chemanim import Protein
import os

class ProteinTraceDemo(Scene):
    def construct(self):
        # Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=0 * DEGREES, phi=70 * DEGREES)
        
        # Title
        title = Text("Protein Trace", font_size=36).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Path setup
        pdb_path = "pdb1crn.ent"
        if not os.path.exists(pdb_path):
             pdb_path = os.path.join("examples", "simple.pdb")

        # Load
        print("Loading Protein Trace...")
        mol = Protein(pdb_path, render_style="trace", include_hydrogens=False)
        mol.scale(1.5)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Animate
        self.play(Rotate(mol, angle=2*PI, axis=UP), run_time=10)
