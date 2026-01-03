"""ManimGL Demo: Protein Ball and Stick
"""
from manimlib import *
from chemanim import Protein
import os

class ProteinSpaceFillDemo(Scene):
    def construct(self):
        # Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=10 * DEGREES, phi=60 * DEGREES)
        
        # Title
        title = Text("Protein Space Filling (CPK)", font_size=36).to_edge(UP)
        subtitle = Text("Optimized Spheres (Low Poly)", font_size=24, color=GREY).next_to(title, DOWN)
        title.fix_in_frame()
        subtitle.fix_in_frame()
        self.add(title, subtitle)
        
        # Path setup
        pdb_path = "pdb1crn.ent"
        if not os.path.exists(pdb_path):
             pdb_path = os.path.join("examples", "simple.pdb")

        # Load
        print("Loading Protein Space Filling...")
        # Use low resolution for better performance with many atoms
        mol = Protein(
            pdb_path, 
            render_style="space_filling", 
            include_hydrogens=False, 
            resolution=(12, 12)
        )
        mol.scale(1.5)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Animate
        self.play(Rotate(mol, angle=2*PI, axis=UP), run_time=10)
