from manimlib import *
from chemanim.reaction import ChemicalReaction

class BondBreakingDemo(Scene):
    def construct(self):
        title = Text("Reaction: CH4 + 2O2 -> CO2 + 2H2O").to_edge(UP)
        self.add(title)

        # Defines reactants and products by name
        # Note: PubChem search for "Oxygen" creates O2 usually? 
        # If not, we might get simple atoms. 
        # "Dioxygen" is safer for O2.
        
        # CH4, O2, O2 -> CO2, H2O, H2O
        reaction = ChemicalReaction(
            reactants_ids=["Methane", "Dioxygen", "Dioxygen"], 
            products_ids=["Carbon Dioxide", "Water", "Water"]
        )
        
        # Position the reaction group (it centers itself at ORIGIN by default)
        # But we might want reactants to start slightly offset if our camera is static?
        # The ChemicalReaction logic puts Reactants at ORIGIN and Products at ORIGIN (target).
        # So the animation happens "in place".
        
        self.add(reaction) # Adds the reactants initially
        self.wait(1)
        
        # Play the reaction animation
        self.play(reaction.animate_reaction(run_time=3))
        
        self.wait(2)
