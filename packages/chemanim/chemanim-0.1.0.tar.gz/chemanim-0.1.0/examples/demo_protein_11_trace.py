"""ManimGL Demo: Protein Backbone Trace"""
from manimlib import *
from chemanim.bio import Protein
import os

class ProteinTraceDemo(Scene):
    def construct(self):
        # Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=0 * DEGREES, phi=90 * DEGREES)  # Top-down view like Mol*
        
        # Title
        title = Text("Protein Backbone Trace", font_size=36).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
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
        
        # Apply trace style (backbone Cα trace)
        print("Creating backbone trace...")
        molecule.apply_render_style("trace")
        
        # Center and scale
        molecule.scale(2.5)
        molecule.move_to(ORIGIN)
        
        self.add(molecule)
        
        # Animate - slow rotation
        self.play(Rotate(molecule, angle=2*PI, axis=UP, run_time=10))
