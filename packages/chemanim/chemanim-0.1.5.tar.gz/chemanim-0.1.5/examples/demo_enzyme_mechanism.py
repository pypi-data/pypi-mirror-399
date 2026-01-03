from manimlib import *
from chemanim import *

class EnzymeMechanismDemo(Scene):
    def construct(self):
        # 1. Setup Title
        title = Text("Enzyme Catalysis Mechanism: Lysozyme", font_size=40)
        title.to_edge(UP)
        self.add(title)
        
        # 2. Load Enzyme (Lysozyme) from UniProt
        # P00698 is Hen Egg White Lysozyme
        # We use 'surface' style to show the shape/pocket
        print("Fetching Lysozyme (P00698)...")
        enzyme = Protein.from_uniprot("P00698", render_style="surface", use_alphafold=True)
        enzyme.scale(1.5)
        # Rotate to show active site better (approximate rotation)
        enzyme.rotate(90 * DEGREES, RIGHT) 
        
        # 3. Setup Enzymatic Reaction
        # Substrate: N-Acetylglucosamine (NAG) - CID 24139
        # Product:  N-Acetylmuramic acid (NAM) - CID 441038 (just as an example transformation)
        # Active site residues for P00698: Glu35, Asp52
        print("Setting up reaction system...")
        reaction = EnzymeReaction(
            enzyme=enzyme,
            substrate_id="24139", 
            product_id="441038",
            active_site_residues=[35, 52] 
        )
        
        # Add Enzyme to scene
        self.play(FadeIn(enzyme))
        self.wait()
        
        # 4. Animate: Substrate Appearance
        # Reactants start at origin, let's move them to start position (left)
        substrate = reaction.reactants_group
        substrate.move_to(LEFT * 5)
        
        label_sub = Text("Substrate (NAG)", font_size=24, color=GREY).next_to(substrate, DOWN)
        label_enz = Text("Enzyme (Lysozyme)", font_size=24, color=BLUE).next_to(enzyme, DOWN)
        
        self.play(
            FadeIn(substrate),
            Write(label_sub),
            Write(label_enz)
        )
        self.wait()
        
        # 5. Animate: Docking
        # Move camera/zoom in for better view
        self.play(
            self.camera.frame.animate.scale(0.6).move_to(enzyme),
            FadeOut(label_sub),
            FadeOut(label_enz),
            title.animate.scale(0.6).to_corner(UL)
        )
        
        dock_text = Text("Docking...", font_size=30, color=YELLOW)
        dock_text.fix_in_frame()
        dock_text.to_corner(UR)
        self.play(Write(dock_text))
        
        self.play(reaction.animate_docking(run_time=3.0))
        self.wait(0.5)
        
        # 6. Animate: Catalysis
        catalysis_text = Text("Catalysis...", font_size=30, color=RED)
        catalysis_text.fix_in_frame()
        catalysis_text.to_corner(UR)
        
        self.play(
            ReplacementTransform(dock_text, catalysis_text),
            reaction.animate_catalysis(run_time=1.5)
        )
        
        # Flash effect to emphasize reaction
        flash = Circle(color=WHITE).scale(0.1).move_to(reaction.products_group.get_center())
        self.play(
            flash.animate.scale(5).set_opacity(0),
            run_time=0.5
        )
        self.wait(0.5)
        
        # 7. Animate: Release
        release_text = Text("Release", font_size=30, color=GREEN)
        release_text.fix_in_frame()
        release_text.to_corner(UR)
        
        self.play(
            ReplacementTransform(catalysis_text, release_text),
            reaction.animate_release(direction=RIGHT + UP, run_time=2.0)
        )
        self.wait()
        
        # 8. Reset View
        self.play(
            self.camera.frame.animate.scale(1/0.6).move_to(ORIGIN),
            FadeOut(release_text)
        )
        self.wait()
