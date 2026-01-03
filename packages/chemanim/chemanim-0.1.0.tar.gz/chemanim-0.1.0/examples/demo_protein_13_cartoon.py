"""ManimGL Demo: Protein Cartoon Render Style"""
from manimlib import *
from chemanim.bio import Protein
import os

class ProteinCartoonDemo(Scene):
    def construct(self):
        # Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        
        # Title
        title = Text("Protein Cartoon Structure", font_size=36).to_edge(UP)
        subtitle = Text("Based on Ribbon Logic", font_size=24, color=GREY).next_to(title, DOWN)
        title.fix_in_frame()
        subtitle.fix_in_frame()
        self.add(title, subtitle)
        
        # Fetch or load PDB
        try:
            print("Fetching 1CRN...")
            molecule = Protein.from_pdb_id("1CRN", download_dir="examples", include_hydrogens=False)
        except Exception as e:
            print(f"Failed to fetch 1CRN: {e}")
            pdb_path = "pdb1crn.ent"
            if not os.path.exists(pdb_path):
                 print("Cannot find PDB file.")
                 return
            molecule = Protein(pdb_path, include_hydrogens=False)
        
        # Apply cartoon style
        print("Creating cartoon...")
        molecule.apply_render_style("cartoon")
        # Enable visible H-bonds
        print("Finding interactions...")
        molecule.toggle_interactions(True)
        
        # Center and scale
        molecule.scale(2.5)
        molecule.move_to(ORIGIN)
        
        self.add(molecule)
        
        # Animate - slow rotation
        self.play(Rotate(molecule, angle=2*PI, axis=UP, run_time=10))
