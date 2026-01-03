from manimlib import *
from chemanim import ChemicalReaction
import os

class LineReactionDemo(Scene):
    def construct(self):
        title = Text("Reaction with Line Structure", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # Methane Combustion: CH4 + 2O2 -> CO2 + 2H2O
        # Using PubChem names.
        
        try:
            reaction = ChemicalReaction(
                reactants_ids=["Methane", "Dioxygen", "Dioxygen"], 
                products_ids=["Carbon Dioxide", "Water", "Water"],
                use_chem_object=True # Enable Line Structure mode!
            )
            
            # Arrange molecules centered to simulate in-place rearrangement
            reaction.reactants_group.arrange(RIGHT, buff=1.0)
            reaction.products_group.arrange(RIGHT, buff=1.0)
            
            reaction.reactants_group.move_to(ORIGIN)
            reaction.products_group.move_to(ORIGIN)
            
            self.add(reaction)
            self.wait(1)
            
            self.play(reaction.animate_reaction(run_time=5.0))
            self.wait(2)
            
        except Exception as e:
            err = Text(f"Error: {e}", font_size=24, color=RED)
            self.add(err)
