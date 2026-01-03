from manimlib import *
from chemanim.core import Molecule
import os

class JsonLoadDemo(Scene):
    def construct(self):
        # Path to the JSON file
        # Assuming run from workspace root
        
        # Absolute path provided by user is 
        # d:\Law\Chemanim\Asset\Structure2D_COMPOUND_CID_280.json
        
        # Determine strict path
        base_path = r"d:\Law\Chemanim"
        json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Could not find file at {json_path}")
            
        title = Text("Loading CO2 from Local JSON", font_size=36).to_edge(UP)
        self.play(Write(title))

        # Create Molecule from JSON
        co2 = Molecule.from_file(json_path)
        co2.scale(2) # Make it bigger
        
        self.play(FadeIn(co2))
        self.wait(1)
        
        # Rotate it to show it's a 3D object (even if coords are 2D, Manim renders it in scene)
        self.play(Rotate(co2, angle=2*PI, axis=UP), run_time=4)
        
        self.wait()
