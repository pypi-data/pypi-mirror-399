from manimlib import *
from chemanim import ChemObject

class SkeletalZigZag(Scene):
    def construct(self):
        title = Text("Skeletal (zigzag)", font_size=36).to_edge(UP)
        self.play(Write(title))

        hexane = ChemObject.from_pubchem("Hexane", bond_length=1.1, zigzag_chain=True, skeletal=True)
        hexane.move_to(LEFT * 3)
        label1 = Text("Hexane skeletal", font_size=18).next_to(hexane, DOWN, buff=0.3)

        propene = ChemObject.from_pubchem("Propene", bond_length=1.1, zigzag_chain=True, skeletal=True)
        propene.move_to(RIGHT * 3)
        label2 = Text("Propene skeletal", font_size=18).next_to(propene, DOWN, buff=0.3)

        self.play(Create(hexane), Write(label1))
        self.play(Create(propene), Write(label2))
        self.wait(3)
