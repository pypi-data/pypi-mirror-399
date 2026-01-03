"""ManimGL Demo: Bio Molecule Fetch

Demonstrates fetching a protein from PDB and rendering it using ManimGL.
"""
from manimlib import *
from chemanim import Macromolecule
import os


class BioFetchDemo(Scene):
    """Protein fetch demo using ManimGL."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=75 * DEGREES)
        
        title = Text("Loading '1CRN' from RCSB PDB").to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Fetch from PDB
        mol = Macromolecule.from_pdb_id("1CRN", render_style="sticks", include_hydrogens=False)
        
        # Center the molecule
        mol.move_to(ORIGIN)
        
        self.add(mol)
        
        self.play(Rotate(mol, PI, axis=UP), run_time=6)
        
        # Switch to trace
        t2 = Text("Backbone Trace").to_corner(UL).scale(0.8)
        t2.fix_in_frame()
        self.add(t2)
        
        mol.apply_render_style("trace")
        self.wait(2)


# Run with ManimGL:
# manimgl examples/demo_bio_fetch.py BioFetchDemo -w
