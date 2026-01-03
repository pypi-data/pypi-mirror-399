from manimlib import *
from chemanim.bio import Protein
import os

class ProteinSurfaceDemo(Scene):
    def construct(self):
        # Try to fetch standard protein 1CRN
        try:
            print("Fetching 1CRN...")
            molecule = Protein.from_pdb_id("1CRN", download_dir="examples", include_hydrogens=False)
        except Exception as e:
            print(f"Failed to fetch 1CRN: {e}")
            # Fallback to local if fetch fails
            pdb_path = "pdb1crn.ent"
            if not os.path.exists(pdb_path):
                 print("Cannot find PDB file.")
                 return
            molecule = Protein(pdb_path, include_hydrogens=False)
        
        # Apply surface style
        print("Generating surface...")
        # Note: This might take a few seconds
        molecule.apply_render_style("surface")
        
        # Center and scale
        molecule.scale(2)
        molecule.move_to(ORIGIN)
        
        # Rotate to show 3D shape
        molecule.rotate(30 * DEGREES, axis=UP)
        molecule.rotate(30 * DEGREES, axis=RIGHT)
        
        self.add(molecule)
        
        # Animate rotation
        self.play(Rotate(molecule, angle=360 * DEGREES, axis=UP, run_time=10))
