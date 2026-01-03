"""ManimGL Demo: Hemoglobin Multi-Chain Protein
Showcases color schemes and render styles on a larger multi-chain protein.
Hemoglobin (2HHB) has 4 chains - 2 alpha and 2 beta subunits.
"""
from manimlib import *
from chemanim.bio import Protein
import os

class HemoglobinShowcase(Scene):
    def construct(self):
        # Camera Setup - Zoomed out significantly for large molecule
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        frame.scale(3.5)  # Zoom out significantly for hemoglobin
        
        # Title
        title = Text("Hemoglobin (4 Chains)", font_size=36).to_edge(UP)
        title.fix_in_frame()
        self.add(title)
        
        # Dynamic label
        info_label = Text("Loading...", font_size=24, color=YELLOW).next_to(title, DOWN)
        info_label.fix_in_frame()
        self.add(info_label)

        # Load Hemoglobin (2HHB - Human Deoxyhemoglobin)
        print("Fetching Hemoglobin (2HHB)...")
        try:
            mol = Protein.from_pdb_id("2HHB", download_dir="examples", include_hydrogens=False)
        except Exception as e:
            print(f"Fetch failed: {e}")
            return

        # Start with cartoon to show structure
        mol.apply_render_style("cartoon")
        mol.scale(1.5)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Initial reveal
        new_label = Text("Cartoon - SSE Coloring", font_size=24, color=YELLOW).next_to(title, DOWN)
        new_label.fix_in_frame()
        self.play(Transform(info_label, new_label), run_time=0.5)
        self.play(Rotate(mol, angle=90 * DEGREES, axis=UP), run_time=2)
        self.wait(0.5)

        # ===== COLOR SCHEMES DEMO =====
        color_schemes = [
            ("chain", "Color by Chain (4 different colors)"),
            ("amino_acid", "Color by Amino Acid Type"),
            ("rainbow", "Rainbow (N→C Terminus per Chain)"),
            ("hydrophobicity", "Hydrophobicity Scale"),
        ]

        for scheme_code, scheme_name in color_schemes:
            new_label = Text(scheme_name, font_size=24, color=YELLOW).next_to(title, DOWN)
            new_label.fix_in_frame()
            self.play(Transform(info_label, new_label), run_time=0.3)
            
            print(f"Applying color scheme: {scheme_code}")
            mol.set_color_scheme(scheme_code)
            
            self.play(Rotate(mol, angle=90 * DEGREES, axis=UP), run_time=2)
            self.wait(0.3)

        # ===== RENDER STYLES DEMO =====
        # Reset to SSE coloring for style showcase
        mol.set_color_scheme("sse")
        
        styles = [
            ("ribbon", "Ribbon Style"),
            ("trace", "Backbone Trace"),
            ("ball_and_stick", "Ball and Stick"),
            ("sticks", "Sticks"),
        ]

        for style_code, style_name in styles:
            new_label = Text(style_name, font_size=24, color=YELLOW).next_to(title, DOWN)
            new_label.fix_in_frame()
            self.play(Transform(info_label, new_label), run_time=0.3)
            
            print(f"Applying style: {style_code}")
            mol.apply_render_style(style_code)
            
            self.play(Rotate(mol, angle=90 * DEGREES, axis=UP), run_time=2)
            self.wait(0.3)

        # Final - back to cartoon with chain coloring
        new_label = Text("Cartoon - Chain Coloring", font_size=24, color=GREEN).next_to(title, DOWN)
        new_label.fix_in_frame()
        self.play(Transform(info_label, new_label), run_time=0.3)
        
        mol.apply_render_style("cartoon")
        mol.set_color_scheme("chain")
        
        self.play(Rotate(mol, angle=360 * DEGREES, axis=UP), run_time=5)
