from manimlib import *
from chemanim import ChemObject
import os

class BondingDemo(Scene):
    def construct(self):
        title = Text("Bond Breaking & Forming", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # 1. Load CO2
        base_path = r"d:\Law\Chemanim"
        json_path = os.path.join(base_path, "Asset", "Structure2D_COMPOUND_CID_280.json")

        co2 = ChemObject.from_file(json_path, font_size=40, bond_length_scale=3.0)
        co2.move_to(ORIGIN)
        self.play(DrawBorderThenFill(co2))
        self.wait()
        
        # Atoms indices for CO2:
        # Based on JSON:
        # 1-based: 1=O, 2=O, 3=C
        # 0-based: 0=O, 1=O, 2=C
        # Bonds: 1-3 (O=C) and 2-3 (O=C)
        # So in 0-based: (0, 2) and (1, 2)
        
        # 2. Break Double Bond (O=C)
        t1 = Text("Breaking Bond...", font_size=24, color=RED).next_to(co2, DOWN)
        self.play(FadeIn(t1))
        
        # Break bond between O(index 0) and C(index 2)
        self.play(co2.break_bond(0, 2))
        self.wait()
        
        # 3. Form new Single Bond
        t2 = Text("Forming Single Bond...", font_size=24, color=GREEN).next_to(co2, DOWN)
        self.play(Transform(t1, t2))
        
        # Re-form bond 0-2 as single
        self.play(co2.form_bond(0, 2, order=1))
        self.wait()
        
        # 4. Form bond between the two Oxygens (Cyclic structure? Unstable but visuals work)
        t3 = Text("Forming O-O Bond (Loop)", font_size=24, color=YELLOW).next_to(co2, DOWN)
        self.play(Transform(t1, t3))
        
        # Bond between O(0) and O(1)
        self.play(co2.form_bond(0, 1, order=1))
        self.wait(2)
