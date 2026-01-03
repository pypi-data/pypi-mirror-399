from manimlib import *
from chemanim import ChemicalReaction, ChemObject

class WaterFormation(Scene):
    """2H2 + O2 -> 2H2O"""
    def construct(self):
        title = Text("Water Formation", font_size=36).to_edge(UP)
        equation = Text("2H₂ + O₂ → 2H₂O", font_size=28).next_to(title, DOWN)
        self.play(Write(title), Write(equation))
        
        try:
            reaction = ChemicalReaction(
                reactants_ids=["Hydrogen", "Hydrogen", "Oxygen"],
                products_ids=["Water", "Water"],
                use_chem_object=True
            )
            
            reaction.reactants_group.arrange(RIGHT, buff=1.0)
            reaction.products_group.arrange(RIGHT, buff=1.0)
            reaction.reactants_group.move_to(ORIGIN)
            reaction.products_group.move_to(ORIGIN)
            
            self.add(reaction)
            self.wait(1)
            self.play(reaction.animate_reaction(run_time=4.0))
            self.wait(2)
            
        except Exception as e:
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)


class AcidBaseNeutralization(Scene):
    """HCl + NaOH -> NaCl + H2O"""
    def construct(self):
        title = Text("Acid-Base Neutralization", font_size=36).to_edge(UP)
        equation = Text("HCl + NaOH → NaCl + H₂O", font_size=28).next_to(title, DOWN)
        self.play(Write(title), Write(equation))
        
        try:
            reaction = ChemicalReaction(
                reactants_ids=["Hydrochloric acid", "Sodium hydroxide"],
                products_ids=["Sodium chloride", "Water"],
                use_chem_object=True
            )
            
            reaction.reactants_group.arrange(RIGHT, buff=1.5)
            reaction.products_group.arrange(RIGHT, buff=1.5)
            reaction.reactants_group.move_to(ORIGIN)
            reaction.products_group.move_to(ORIGIN)
            
            self.add(reaction)
            self.wait(1)
            self.play(reaction.animate_reaction(run_time=4.0))
            self.wait(2)
            
        except Exception as e:
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)


class AmmoniaFormation(Scene):
    """N2 + 3H2 -> 2NH3 (Haber Process)"""
    def construct(self):
        title = Text("Haber Process (Ammonia Synthesis)", font_size=36).to_edge(UP)
        equation = Text("N₂ + 3H₂ → 2NH₃", font_size=28).next_to(title, DOWN)
        self.play(Write(title), Write(equation))
        
        try:
            reaction = ChemicalReaction(
                reactants_ids=["Nitrogen", "Hydrogen", "Hydrogen", "Hydrogen"],
                products_ids=["Ammonia", "Ammonia"],
                use_chem_object=True
            )
            
            reaction.reactants_group.arrange(RIGHT, buff=0.8)
            reaction.products_group.arrange(RIGHT, buff=0.8)
            reaction.reactants_group.move_to(ORIGIN)
            reaction.products_group.move_to(ORIGIN)
            
            self.add(reaction)
            self.wait(1)
            
            # Get the animation and play it
            anim = reaction.animate_reaction(run_time=4.0)
            if anim:
                self.play(anim)
            self.wait(2)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)


class EthanolCombustion(Scene):
    """C2H5OH + 3O2 -> 2CO2 + 3H2O"""
    def construct(self):
        title = Text("Ethanol Combustion", font_size=36).to_edge(UP)
        equation = Text("C₂H₅OH + 3O₂ → 2CO₂ + 3H₂O", font_size=28).next_to(title, DOWN)
        self.play(Write(title), Write(equation))
        
        try:
            reaction = ChemicalReaction(
                reactants_ids=["Ethanol", "Oxygen", "Oxygen", "Oxygen"],
                products_ids=["Carbon dioxide", "Carbon dioxide", "Water", "Water", "Water"],
                use_chem_object=True
            )
            
            reaction.reactants_group.arrange(RIGHT, buff=0.6)
            reaction.products_group.arrange(RIGHT, buff=0.6)
            reaction.reactants_group.move_to(ORIGIN)
            reaction.products_group.move_to(ORIGIN)
            
            self.add(reaction)
            self.wait(1)
            self.play(reaction.animate_reaction(run_time=5.0))
            self.wait(2)
            
        except Exception as e:
            err = Text(f"Error: {e}", font_size=20, color=RED)
            self.add(err)
