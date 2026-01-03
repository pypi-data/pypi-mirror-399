from manimlib import *
from chemanim.core import Molecule

class PubChemDemo(Scene):
    def construct(self):
        t = Text("Loading from PubChem...").to_edge(UP)
        self.add(t)
        
        try:
            # Fetch Caffeine
            caffeine = Molecule.from_pubchem("caffeine")
            caffeine.scale(0.5)
            
            self.remove(t)
            name = Text("Caffeine").to_edge(UP)
            self.play(Write(name), Create(caffeine))
            
            self.play(Rotate(caffeine, angle=PI, axis=RIGHT))
            self.wait()
            
            self.play(FadeOut(caffeine), FadeOut(name))
            
            # Fetch Aspirin
            aspirin = Molecule.from_pubchem("aspirin")
            aspirin.scale(0.5)
            name2 = Text("Aspirin").to_edge(UP)
            
            self.play(Write(name2), Create(aspirin))
            self.wait()
            
        except Exception as e:
            err = Text(f"Error: {e}", font_size=24, color=RED)
            self.add(err)
            self.wait(3)
