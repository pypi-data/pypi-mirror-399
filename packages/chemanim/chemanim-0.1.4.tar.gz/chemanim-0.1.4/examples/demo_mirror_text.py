from manimlib import *
from chemanim import ChemObject
import os

class MirrorDemo(Scene):
    def construct(self):
        # 1. Load C02
        base_path = r"d:\Law\Chemanim"
        json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")

        title = Text("Mirroring without Rotating Text", font_size=36).to_edge(UP)
        self.add(title)
        
        # Load object
        co2 = ChemObject.from_file(json_path, font_size=40)
        co2.move_to(ORIGIN)
        
        self.add(co2)
        
        # 2. Mirror Vertical (Default: Text stays upright)
        # Carbon labels (O=C=O) are symmetric so hard to see flipping back.
        # But if 'C' was flipped, it would look backward.
        
        self.wait()
        self.play(co2.animate.mirror_vertical(rotate_text=False))
        self.wait()
        
        desc = Text("Vertical Flip (Text Corrected)", font_size=24, color=YELLOW).next_to(co2, DOWN)
        self.play(FadeIn(desc))
        self.wait(2)
        
        # 3. Rotate Molecule (Text Corrected)
        self.play(Rotate(co2, angle=PI/4), run_time=2)
        desc2 = Text("Rotation (Text Rotated)", font_size=24, color=RED).next_to(co2, DOWN)
        self.play(Transform(desc, desc2))
        
        # Now explicit rotate with correction (simulated by method call immediately)
        # Note: 'animate' wrapper calls method but logic runs frame by frame or end state? 
        # Manim's .animate usually interpolates properties.
        # Complex structural logic (looping over sub-mobjects and flipping them) might not interpolate well with .animate
        # Better to do it directly.
        
        co2_rot_fixed = co2.copy()
        co2_rot_fixed.rotate_molecule(PI/4, rotate_text=False)
        co2_rot_fixed.move_to(RIGHT*4)
        
        self.play(TransformFromCopy(co2, co2_rot_fixed))
        self.add(Text("Rotated + Fixed Text", font_size=20).next_to(co2_rot_fixed, DOWN))
        self.wait(2)
