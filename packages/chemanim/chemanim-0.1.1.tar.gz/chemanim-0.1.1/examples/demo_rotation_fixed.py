from manimlib import *
from chemanim import ChemObject
import os

class RotationFixedTextDemo(Scene):
    def construct(self):
        # 1. Load Benzene (good for rotation test)
        # Using local mock if internet fails, but let's try just manual CO2 first as requested or Benzene from PubChem
        
        title = Text("Rotation with Fixed Text (Default)", font_size=36).to_edge(UP)
        self.add(title)

        try:
            # Try load Benzene
            benzene = ChemObject.from_pubchem("benzene")
        except:
            # Fallback to local CO2
            base_path = r"d:\Law\Chemanim"
            json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")
            benzene = ChemObject.from_file(json_path)

        benzene.move_to(ORIGIN)
        self.add(benzene)
        self.wait()
        
        # 2. Rotate 90 degrees
        # Default behavior: Structure rotates, 'C' / 'H' text stays upright
        self.play(benzene.animate.rotate_molecule(PI/2))
        self.wait()
        
        desc = Text("Rotated 90 deg (Text Upright)", font_size=24, color=GREEN).next_to(benzene, DOWN)
        self.play(FadeIn(desc))
        self.wait()
        
        # 3. Continuous Rotation
        # Note: animate.rotate_molecule might not trigger the internal fix logic if Manim only interpolates points.
        # Custom updater is better for continuous logic.
        
        self.play(Rotate(benzene, angle=PI, about_point=benzene.get_center()), run_time=2)
        # Standard Rotate(...) blindly rotates everything.
        # Our .rotate_molecule() has the fix logic.
        # So we should use a value tracker + updator to use our method if we want smooth animation with fixed text.
        
        # BUT for step-wise animation, just calling .animate.rotate_molecule(...) works if the method returns self.
        
        # Let's show explicit non-fixed rotation for comparison
        self.play(benzene.animate.rotate_molecule(PI/2, rotate_text=True))
        
        desc2 = Text("Text Rotated (Opt-in)", font_size=24, color=RED).next_to(benzene, DOWN)
        self.play(Transform(desc, desc2))
        self.wait(2)
