"""ManimGL Demo: Protein Color Schemes (Ball and Stick)
"""
from manimlib import *
from chemanim.bio import Protein
import os

class ProteinColorDemo(Scene):
    def construct(self):
        # Camera Setup
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        
        # Title
        title = Text("Protein Color Schemes", font_size=40).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Dynamic Label for Theme
        current_theme_text = "Secondary Structure (Default)"
        theme_label = Text(current_theme_text, font_size=24, color=YELLOW).next_to(title, DOWN)
        theme_label.fix_in_frame()
        self.add(theme_label)

        # Load Protein (1CRN - Crambin)
        print("Fetching 1CRN...")
        try:
            mol = Protein.from_pdb_id("1CRN", download_dir="examples", include_hydrogens=False)
        except Exception as e:
            print(f"Fetch failed: {e}. Trying local file...")
            mol = Protein("pdb1crn.ent", include_hydrogens=False)

        # Apply Ball and Stick Style (using SSE as base so we have a valid starting scheme)
        mol.apply_render_style("ball_and_stick_sse") 
        mol.scale(2.5)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Initial Animation
        self.play(ShowCreation(mol), run_time=2)
        self.wait(1)

        # List of schemes to cycle through
        schemes = [
            ("sse", "Secondary Structure"),
            ("chain", "By Chain ID"),
            ("amino_acid", "Amino Acid Type"),
            ("rainbow", "Rainbow (N-Terminus -> C-Terminus)"),
            ("hydrophobicity", "Hydrophobicity (Blue=Hydrophilic, Red=Hydrophobic)"),
            ("asa", "Accessible Surface Area (Grey=Buried, Red=Exposed)")
        ]

        for code, name in schemes:
            # Create new label
            new_label = Text(name, font_size=24, color=YELLOW).next_to(title, DOWN)
            new_label.fix_in_frame()
            
            # Switch Text
            self.play(
                Transform(theme_label, new_label),
                run_time=0.5
            )
            theme_label = new_label # Update reference

            # Apply Color Scheme
            print(f"Applying scheme: {code}")
            mol.set_color_scheme(code)
            
            # Rotate to showcase
            self.play(
                Rotate(mol, angle=90 * DEGREES, axis=UP),
                run_time=2.0
            )
            self.wait(0.5)

        # Final Spin
        self.play(Rotate(mol, angle=360 * DEGREES, axis=UP), run_time=5)
