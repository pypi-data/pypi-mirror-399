from manimlib import *
from chemanim import ChemObject

class StraightChainDemo(Scene):
    """Demo comparing VSEPR, straight chain, and zigzag chain modes"""
    def construct(self):
        title = Text("Chain Geometry Modes", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        try:
            # Butane comparison - 3 modes
            butane_vsepr = ChemObject.from_pubchem("Butane", bond_length=0.8)
            butane_vsepr.move_to(LEFT * 4 + UP * 0.5)
            label1 = Text("VSEPR", font_size=20).next_to(butane_vsepr, DOWN, buff=0.3)
            
            butane_straight = ChemObject.from_pubchem("Butane", bond_length=0.8, straight_chain=True)
            butane_straight.move_to(ORIGIN + UP * 0.5)
            label2 = Text("straight_chain", font_size=20).next_to(butane_straight, DOWN, buff=0.3)
            
            butane_zigzag = ChemObject.from_pubchem("Butane", bond_length=0.8, zigzag_chain=True)
            butane_zigzag.move_to(RIGHT * 4 + UP * 0.5)
            label3 = Text("zigzag_chain", font_size=20).next_to(butane_zigzag, DOWN, buff=0.3)
            
            self.play(
                Create(butane_vsepr), Create(butane_straight), Create(butane_zigzag),
                Write(label1), Write(label2), Write(label3)
            )
            self.wait(3)
            
            # Clear and show Ethanol
            self.play(
                FadeOut(butane_vsepr), FadeOut(butane_straight), FadeOut(butane_zigzag),
                FadeOut(label1), FadeOut(label2), FadeOut(label3)
            )
            
            eth_vsepr = ChemObject.from_pubchem("Ethanol", bond_length=1.0)
            eth_vsepr.move_to(LEFT * 4)
            label4 = Text("VSEPR", font_size=20).next_to(eth_vsepr, DOWN, buff=0.3)
            
            eth_straight = ChemObject.from_pubchem("Ethanol", bond_length=1.0, straight_chain=True)
            eth_straight.move_to(ORIGIN)
            label5 = Text("straight_chain", font_size=20).next_to(eth_straight, DOWN, buff=0.3)
            
            eth_zigzag = ChemObject.from_pubchem("Ethanol", bond_length=1.0, zigzag_chain=True)
            eth_zigzag.move_to(RIGHT * 4)
            label6 = Text("zigzag_chain", font_size=20).next_to(eth_zigzag, DOWN, buff=0.3)
            
            self.play(
                Create(eth_vsepr), Create(eth_straight), Create(eth_zigzag),
                Write(label4), Write(label5), Write(label6)
            )
            self.wait(3)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)
