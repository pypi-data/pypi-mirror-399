"""ManimGL Demo: Protein Visualization

Demonstrates various render styles for proteins using ManimGL.
"""
from manimlib import *
from chemanim.bio import Protein
import os


class ProteinDemo(Scene):
    """Protein visualization demo using ManimGL."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=60 * DEGREES)
        
        pdb_path = os.path.join(os.path.dirname(__file__), "simple.pdb")
        
        # Title
        title = Text("Protein Visualization").to_edge(UP)
        title.fix_in_frame()
        self.add(title)

        # Load Molecule
        mol = Protein(pdb_path, render_style="sticks")
        self.add(mol)
        
        # Rotate
        self.play(Rotate(mol, PI/2, axis=UP), run_time=2)
        
        # Switch to Ball and Stick
        t1 = Text("Ball and Stick").to_corner(UL).scale(0.7)
        t1.fix_in_frame()
        self.play(FadeIn(t1))
        
        mol.apply_render_style("ball_and_stick")
        self.wait(1)
        
        # Switch to Space Filling
        t2 = Text("Space Filling").to_corner(UL).scale(0.7)
        t2.fix_in_frame()
        self.remove(t1)
        self.add(t2)
        
        mol.apply_render_style("space_filling")
        self.wait(1)
        
        # Switch to Trace (Backbone)
        t3 = Text("Backbone Trace").to_corner(UL).scale(0.7)
        t3.fix_in_frame()
        self.remove(t2)
        self.add(t3)
        
        mol.apply_render_style("trace")
        self.wait(1)
        
        # Back to sticks
        t4 = Text("Sticks").to_corner(UL).scale(0.7)
        t4.fix_in_frame()
        self.remove(t3)
        self.add(t4)
        
        mol.apply_render_style("sticks")
        self.wait(1)
        
        # ManimGL: animate camera frame
        self.play(frame.animate.set_euler_angles(theta=-45 * DEGREES), run_time=2)


# Run with ManimGL:
# manimgl examples/demo_protein.py ProteinDemo -w
