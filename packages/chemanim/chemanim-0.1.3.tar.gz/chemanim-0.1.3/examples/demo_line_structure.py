from manimlib import *
from chemanim import ChemObject
import os

class LineStructureDemo(Scene):
    def construct(self):
        # 1. Load CO2 from Local File
        base_path = r"d:\Law\Chemanim"
        json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")

        title = Text("Line Structure (2D Diagram)", font_size=36).to_edge(UP)
        self.add(title)

        if os.path.exists(json_path):
            label1 = Text("From Local JSON:", font_size=24, color=GREY).shift(UP*1.5 + LEFT*3)
            self.add(label1)
            
            # Create CObject (ChemObject)
            co2_local = ChemObject.from_file(json_path)
            co2_local.move_to(LEFT*3)
            self.play(Write(co2_local))
        
        # 2. Load Benzene from PubChem (to show 2D ring structure)
        # Assuming internet is available and pubchempy works
        label2 = Text("From PubChem (Benzene):", font_size=24, color=GREY).shift(UP*1.5 + RIGHT*3)
        self.add(label2)
        
        try:
            benzene = ChemObject.from_pubchem("benzene")
            benzene.move_to(RIGHT*3)
            
            # PubChem 2D coords come normalized/centered usually, but scaling might be needed
            # Our ChemObject scales by 2.5 by default in _build.
            
            self.play(Create(benzene))
        except Exception as e:
            err = Text("Could not load Benzene", color=RED).move_to(RIGHT*3)
            self.add(err)
            print(e)
            
        self.wait(2)
        
        # Animate transforming CO2 to Benzene (Just for fun visual, not chemical reality)
        if os.path.exists(json_path):
             self.play(Transform(co2_local, benzene))
             self.wait()
