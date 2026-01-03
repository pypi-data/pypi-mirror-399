"""ManimGL Demo: Protein Render Styles

Demonstrates all supported protein rendering styles:
- Trace (Backbone tube)
- Cartoon (Secondary structure)
- Ribbon (Flat backbone ribbon)
- Space Filling (Van der Waals spheres)
- Ball and Stick (Atoms and bonds)
- Line (Wireframe)
"""
from manimlib import *
from chemanim import Protein
import os

class ProteinStylesDemo(Scene):
    def construct(self):
        # Setup Camera
        frame = self.camera.frame
        frame.set_euler_angles(theta=0 * DEGREES, phi=70 * DEGREES)
        
        # Title
        title_text = "Protein Render Styles"
        title = Text(title_text, font_size=36).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Load Protein
        # Try local file first, else fallback
        pdb_path = "pdb1crn.ent"
        if not os.path.exists(pdb_path):
             pdb_path = os.path.join("examples", "simple.pdb")
             
        # Start with Trace to ensure it builds first
        print(f"Loading {pdb_path}...")
        try:
            mol = Protein(pdb_path, render_style="trace", include_hydrogens=False)
            mol.scale(1.5)
            mol.move_to(ORIGIN)
            self.add(mol)
            
            # Define styles to cycle through
            # Format: (Display Name, Style Key)
            styles = [
                ("Trace", "trace"),
                ("Cartoon", "cartoon"),
                ("Ribbon", "ribbon"),
                ("Space Filling", "space_fill"),
                ("Ball and Stick", "ball_and_stick"),
                ("Line", "wire"),
            ]
            
            # Loop through styles
            for name, style in styles:
                # Update Title
                new_title = Text(f"Style: {name}", font_size=36).to_edge(UP)
                new_title.fix_in_frame()
                
                self.play(Transform(title, new_title), run_time=0.5)
                
                # Apply Style
                # We do this inside a 'play' via a callback or just immediately?
                # Immediate change is safest for geometry swaps, then rotate.
                mol.apply_render_style(style)
                
                # Rotate for a bit to show it off
                self.play(Rotate(mol, angle=PI/2, axis=UP), run_time=2.0)
                self.wait(0.5)
                
        except Exception as e:
            err = Text(f"Error: {e}", color=RED, font_size=24)
            err.fix_in_frame()
            self.add(err)
            self.wait(5)
            import traceback
            traceback.print_exc()

# Run with:
# manimgl examples/demo_protein_styles.py ProteinStylesDemo -w
