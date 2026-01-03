from manimlib import *
from chemanim.core import Atom, Molecule, Bond

class ReactionDemo(Scene):
    def construct(self):
        self.synthesis_demo()
        self.wait()
        self.clear()
        self.displacement_demo()

    def synthesis_demo(self):
        title = Text("Synthesis: 2H + O -> H2O").to_edge(UP)
        self.play(Write(title))

        # Reactants: 2 H and 1 O
        h1 = Atom(1).shift(LEFT * 3)
        h2 = Atom(1).shift(LEFT * 1.5)
        o1 = Atom(8).shift(RIGHT * 1) # Oxygen
        
        reactants = VGroup(h1, h2, o1)
        self.play(FadeIn(reactants))
        self.wait()

        # Product: Water (H2O)
        # Note: In real Manim, we would animate the position change.
        # Here we create the target molecule
        o_prod = Atom(8)
        h1_prod = Atom(1).move_to(o_prod.get_center() + LEFT*0.8 + DOWN*0.5)
        h2_prod = Atom(1).move_to(o_prod.get_center() + RIGHT*0.8 + DOWN*0.5)
        
        bond1 = Bond(o_prod, h1_prod)
        bond2 = Bond(o_prod, h2_prod)
        
        water = Molecule(atoms=[o_prod, h1_prod, h2_prod], bonds=[bond1, bond2])
        water.move_to(ORIGIN)

        self.play(
            Transform(h1, h1_prod),
            Transform(h2, h2_prod),
            Transform(o1, o_prod),
            Create(bond1),
            Create(bond2)
        )
        self.wait(2)
        self.play(FadeOut(title), FadeOut(h1), FadeOut(h2), FadeOut(o1), FadeOut(bond1), FadeOut(bond2))

    def displacement_demo(self):
        title = Text("Single Displacement: A + BC -> AC + B").to_edge(UP)
        self.play(Write(title))
        
        # Reactants: Na + HCl
        na = Atom(11).shift(LEFT*3) # Sodium
        
        h = Atom(1)
        cl = Atom(17)
        h.shift(LEFT*0.5)
        cl.shift(RIGHT*0.5)
        bond_hcl = Bond(h, cl)
        hcl = Molecule(atoms=[h,cl], bonds=[bond_hcl]).shift(RIGHT*1)
        
        self.play(FadeIn(na), FadeIn(hcl))
        self.wait()
        
        # Products: NaCl + H
        # Na replaces H
        na_prod = Atom(11).move_to(cl.get_center() + LEFT*1.0) # Move Na to where H was (roughly)
        cl_target = cl.copy() # Cl stays roughly there
        bond_nacl = Bond(na_prod, cl_target)
        
        h_prod = Atom(1).shift(RIGHT*3) # H kicked out
        
        self.play(
            Transform(na, na_prod),
            Transform(hcl, cl_target), # Transform HCl group to just Cl? 
            # In simple transform, this might look weird.
            # Better:
            # 1. Break bond
             Uncreate(bond_hcl),
        )
        self.play(
            Transform(h, h_prod),
            Transform(na, na_prod),
            Create(bond_nacl)
        )
        
        self.wait(2)
