from manimlib import *
from chemanim import ChemObject
import os

class CObjectCustomizationDemo(Scene):
    def construct(self):
        # 1. Load C02
        base_path = r"d:\Law\Chemanim"
        json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")

        title = Text("Customizable ChemObject", font_size=36).to_edge(UP)
        self.add(title)
        
        # Initial create
        co2 = ChemObject.from_file(json_path, font_size=32, bond_length_scale=2.0)
        co2.move_to(ORIGIN)
        
        self.add(Text("Original", font_size=20).next_to(co2, DOWN))
        self.play(DrawBorderThenFill(co2))
        self.wait()
        
        # 2. Adjust Parameters Dynamicall
        
        # Scale Bond Length (Spread atoms apart)
        self.play(
            co2.animate.set_bond_length(3.5).set_position(LEFT*3),
            run_time=1.5
        )
        t1 = Text("Long Bonds", font_size=20).next_to(co2, DOWN)
        self.add(t1)
        self.wait()

        # Scale Font Size (Make atoms big)
        # We need a new instance or a manual updater usually for pure Manim transform,
        # but our redraw logic replaces sub-mobjects. 
        # Manim's 'animate' wrapper might not catch the internal redraw if it modifies hierarchy directly 
        # unless we use .animate syntax carefully or custom update function.
        # Since 'set_bond_length' modifies self.submobjects directly immediately, 
        # doing it inside .animate might strictly interpolate Mobject properties but not structure.
        # For structural changes, we usually just do `obj.set_...` then `self.wait()` if it's instant,
        # or use a Transform(old, new).
        
        # Let's create a NEW styled object and Transform to it for smooth animation
        co2_styled = ChemObject.from_file(json_path, font_size=60, bond_length_scale=2.0)
        co2_styled.move_to(RIGHT*3)
        co2_styled.set_color(YELLOW) # Global color (Manim standard)
        
        self.play(Transform(co2.copy(), co2_styled))
        t2 = Text("Big Text", font_size=20).next_to(co2_styled, DOWN)
        self.add(t2, co2_styled)
        self.wait()

        # 3. Mirroring
        # Create an asymmetrical molecule (e.g. from scratch or loaded)
        # Using Benzene locally (simulated dummy if not connected, but let's use CO2 vertical/horiz flip)
        
        co2_flipped = co2_styled.copy().move_to(DOWN*2)
        co2_flipped.mirror_vertical() # Flips UP/DOWN
        # CO2 is symmetric so hard to see.
        # Let's just text label it
        t3 = Text("Mirrored (Vertical)", font_size=20).next_to(co2_flipped, DOWN)
        
        self.play(TransformFromCopy(co2_styled, co2_flipped))
        self.add(t3)
        self.wait()
        
        # 4. Rotation
        self.play(Rotate(co2_flipped, angle=PI/4))
        self.wait(1)

