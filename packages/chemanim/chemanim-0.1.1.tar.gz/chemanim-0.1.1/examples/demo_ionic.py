from manimlib import *
from chemanim import ChemObject

class IonicDemo(Scene):
    def construct(self):
        title = Text("Ionic Compounds", font_size=36).to_edge(UP)
        self.play(Write(title))

        # Sodium Chloride (Na Cl)
        # PubChem "Sodium chloride" (CID 5234) is usually Na+ Cl-
        try:
            nacl = ChemObject.from_pubchem("Sodium chloride")
            nacl.move_to(UP*2)
            label1 = Text("Sodium Chloride (NaCl)", font_size=24).next_to(nacl, DOWN)
            self.play(Create(nacl), Write(label1))
        except Exception as e:
            print(f"Error NaCl: {e}")

        # Sodium Acetate
        try:
            na_acetate = ChemObject.from_pubchem("Sodium acetate")
            na_acetate.move_to(DOWN*1)
            label2 = Text("Sodium Acetate", font_size=24).next_to(na_acetate, DOWN)
            self.play(Create(na_acetate), Write(label2))
        except Exception as e:
            print(f"Error Sodium Acetate: {e}")

        self.wait(3)
