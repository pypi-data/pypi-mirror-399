"""ManimGL Demo: Cartoon Rendering

Demonstrates cartoon (secondary structure) rendering for proteins using ManimGL.
"""
from manimlib import *
from chemanim import Macromolecule
import os


class CartoonDemo(Scene):
    """Protein cartoon rendering demo using ManimGL."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=10 * DEGREES, phi=60 * DEGREES)
        
        # Title
        title = Text("Cartoon Rendering with Biotite").to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Load 1CRN
        print("Using local simple.pdb for test...")
        
        pdb_path = "pdb1crn.ent"
        if not os.path.exists(pdb_path):
             pdb_path = os.path.join("examples", "simple.pdb")
        
        # Load with Cartoon style
        print(f"Loading {pdb_path}...")
        try:
            mol = Macromolecule(pdb_path, render_style="cartoon", include_hydrogens=False)
            mol.scale(1.0)  # Reduced to fit entire protein in view
            mol.move_to(ORIGIN)
            self.add(mol)
            
            # Initial Rotation
            self.play(Rotate(mol, 2*PI, axis=UP), run_time=5)
            
            # Add Legend with JSmol-style colors
            t_a = Text("Alpha Helix", color="#E91E63").scale(0.6).to_corner(UL)
            t_b = Text("Beta Sheet", color="#CFB53B").scale(0.6).next_to(t_a, DOWN)
            t_c = Text("Coil", color="#9E9E9E").scale(0.6).next_to(t_b, DOWN)
            
            legend = VGroup(t_a, t_b, t_c)
            legend.fix_in_frame()
            self.play(FadeIn(legend))
            self.wait(2)
            
        except Exception as e:
            err = Text(f"Error: {e}", color=RED).scale(0.5)
            err.fix_in_frame()
            self.add(err)
            self.wait(5)
            import traceback
            traceback.print_exc()


# Run with ManimGL:
# manimgl examples/demo_cartoon.py CartoonDemo -w
