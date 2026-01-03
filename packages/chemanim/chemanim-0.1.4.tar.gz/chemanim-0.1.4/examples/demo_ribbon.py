"""ManimGL Demo: Protein Ribbon Structure

Demonstrates the ribbon rendering style for proteins using ManimGL.
"""
from manimlib import *
from chemanim import Macromolecule
import os


class ProteinRibbonDemo(ThreeDScene):
    """Protein ribbon structure demo using ManimGL."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=75 * DEGREES)
        
        title = Text("Protein Ribbon Structure (1CRN)").to_edge(UP)
        title.fix_in_frame()  # ManimGL: keep text facing camera
        self.add(title)
        
        print("Fetching 1CRN...")
        # 1CRN is a classic small protein (Crambin) good for demos
        mol = Macromolecule.from_pdb_id("1CRN", render_style="ribbon", include_hydrogens=False)
        mol.scale(3.0)  # Zoom in
        mol.move_to(ORIGIN)
        
        self.add(mol)
        
        # Rotate
        self.play(Rotate(mol, 2*PI, axis=UP), run_time=6)
        
        # Compare with sticks
        t1 = Text("Sticks").to_corner(UL).scale(0.8)
        t1.fix_in_frame()
        self.play(FadeIn(t1))
        
        mol.apply_render_style("sticks")
        self.wait(1.5)
        
        # Back to Ribbon
        t2 = Text("Ribbon").to_corner(UL).scale(0.8)
        t2.fix_in_frame()
        self.remove(t1)
        self.add(t2)
        
        mol.apply_render_style("ribbon")
        self.wait(2)
        
        # ManimGL: animate camera frame
        self.play(frame.animate.set_euler_angles(theta=-45 * DEGREES), run_time=2)


class ProteinTraceDemo(ThreeDScene):
    """Trace-only view of 1CRN backbone."""

    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=25 * DEGREES, phi=70 * DEGREES)

        title = Text("Protein Trace (1CRN)").to_edge(UP)
        title.fix_in_frame()
        self.add(title)

        mol = Macromolecule.from_pdb_id("1CRN", render_style="trace", include_hydrogens=False)
        mol.scale(3.0)
        mol.move_to(ORIGIN)
        self.add(mol)

        caption = Text("Backbone trace").to_corner(UL).scale(0.8)
        caption.fix_in_frame()
        self.play(FadeIn(caption))

        self.play(Rotate(mol, 1.5 * PI, axis=UP), run_time=5)
        self.play(frame.animate.set_euler_angles(theta=-35 * DEGREES), run_time=2)
        self.wait(1)

        self.play(FadeOut(caption), FadeOut(title), FadeOut(mol))
