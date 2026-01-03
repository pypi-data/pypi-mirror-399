"""ManimGL Demo: Protein Render Styles Showcase
Cycles through all available render styles for 1CRN.
"""
from manimlib import *
from chemanim.bio import Protein
import os

class ProteinStylesShowcase(Scene):
    def construct(self):
        # Camera Setup - Zoomed out to see entire structure
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        frame.scale(1.8)  # Zoom out
        
        # Title
        title = Text("Protein Render Styles", font_size=40).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Dynamic label for current style
        style_label = Text("Loading...", font_size=28, color=YELLOW).next_to(title, DOWN)
        style_label.fix_in_frame()
        self.add(style_label)

        # Load Protein (1CRN - Crambin)
        print("Fetching 1CRN...")
        try:
            mol = Protein.from_pdb_id("1CRN", download_dir="examples", include_hydrogens=False)
        except Exception as e:
            print(f"Fetch failed: {e}. Trying local file...")
            mol = Protein("pdb1crn.ent", include_hydrogens=False)

        # Start with trace style (simplest)
        mol.apply_render_style("trace")
        mol.scale(2.0)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # List of styles to showcase
        styles = [
            ("trace", "Backbone Trace"),
            ("ribbon", "Ribbon"),
            ("cartoon", "Cartoon (SSE)"),
            ("ball_and_stick", "Ball and Stick"),
            ("sticks", "Sticks"),
            ("wire", "Wire (Line)"),
            ("space_filling", "Space Filling (CPK)"),
            ("surface", "Molecular Surface"),
        ]

        for style_code, style_name in styles:
            # Update label
            new_label = Text(style_name, font_size=28, color=YELLOW).next_to(title, DOWN)
            new_label.fix_in_frame()
            
            self.play(
                Transform(style_label, new_label),
                run_time=0.3
            )
            
            # Apply style
            print(f"Applying style: {style_code}")
            mol.apply_render_style(style_code)
            
            # Brief pause to show style
            self.wait(0.5)
            
            # Rotate to showcase
            self.play(
                Rotate(mol, angle=120 * DEGREES, axis=UP),
                run_time=2.0
            )
            self.wait(0.3)

        # Final full rotation
        final_label = Text("Complete!", font_size=28, color=GREEN).next_to(title, DOWN)
        final_label.fix_in_frame()
        self.play(Transform(style_label, final_label), run_time=0.3)
        
        self.play(Rotate(mol, angle=360 * DEGREES, axis=UP), run_time=4)
