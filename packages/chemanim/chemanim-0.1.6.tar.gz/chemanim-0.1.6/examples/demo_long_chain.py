from manimlib import *
from chemanim import ChemObject

class LongChainDemo(Scene):
    """Demo with alkanes: Ethane (2C) and Hexane (6C)"""
    def construct(self):
        title = Text("Alkane Chain Comparison", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        try:
            # Ethane (C2H6) - 2 carbon chain
            ethane_straight = ChemObject.from_pubchem("Ethane", bond_length=1.2, straight_chain=True)
            ethane_straight.move_to(LEFT * 4 + UP * 0.5)
            label1 = Text("Ethane C2H6 (straight)", font_size=18).next_to(ethane_straight, DOWN, buff=0.3)
            
            ethane_zigzag = ChemObject.from_pubchem("Ethane", bond_length=1.2, zigzag_chain=True)
            ethane_zigzag.move_to(RIGHT * 4 + UP * 0.5)
            label2 = Text("Ethane C2H6 (zigzag)", font_size=18).next_to(ethane_zigzag, DOWN, buff=0.3)
            
            self.play(
                Create(ethane_straight), Create(ethane_zigzag),
                Write(label1), Write(label2)
            )
            self.wait(3)
            
            # Clear
            self.play(
                FadeOut(ethane_straight), FadeOut(ethane_zigzag),
                FadeOut(label1), FadeOut(label2)
            )
            
            # Hexane (C6H14) - 6 carbon chain
            hexane_straight = ChemObject.from_pubchem("Hexane", bond_length=0.9, straight_chain=True)
            hexane_straight.move_to(UP * 1.5)
            label3 = Text("Hexane C6H14 (straight)", font_size=18).next_to(hexane_straight, DOWN, buff=0.3)
            
            hexane_zigzag = ChemObject.from_pubchem("Hexane", bond_length=0.9, zigzag_chain=True)
            hexane_zigzag.move_to(DOWN * 1.5)
            label4 = Text("Hexane C6H14 (zigzag)", font_size=18).next_to(hexane_zigzag, DOWN, buff=0.3)
            
            self.play(
                Create(hexane_straight), Create(hexane_zigzag),
                Write(label3), Write(label4)
            )
            self.wait(3)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)
