from manimlib import *
from chemanim import ChemObject

class MultiObjectTransformDemo(Scene):
    """
    Demonstrates treating molecules as independent objects:
    - Moving
    - Rotating
    - Scaling
    - Grouping
    """
    def construct(self):
        title = Text("Multiple Independent Objects", font_size=36).to_edge(UP)
        self.play(Write(title))

        # 1. Create two separate molecules
        try:
            water = ChemObject.from_pubchem("Water")
            water.move_to(LEFT * 4)
            label1 = Text("Water", font_size=24).next_to(water, DOWN)
            
            # Use separate instance
            methane = ChemObject.from_pubchem("Methane")
            methane.move_to(RIGHT * 4)
            label2 = Text("Methane", font_size=24).next_to(methane, DOWN)
            
            self.play(
                Create(water), Write(label1),
                Create(methane), Write(label2)
            )
            self.wait(1)

            # 2. Transform independently
            # Rotate Water only
            self.play(
                Rotate(water, angle=PI/2),
                label1.animate.next_to(water, DOWN) # keep label with it? Or just let it be separate
            )
            
            # Scale Methane only
            self.play(
                methane.animate.scale(1.5),
                label2.animate.next_to(methane, DOWN, buff=0.5) # Re-adjust label
            )
            self.wait(1)
            
            # 3. Move independently
            self.play(
                water.animate.move_to(LEFT * 2 + UP * 1),
                methane.animate.move_to(RIGHT * 2 + UP * 1),
                FadeOut(label1), FadeOut(label2)
            )
            
            # 4. Interact / Group behavior
            # Now treat them as a VGroup to rotate together
            physics_group = VGroup(water, methane)
            
            self.play(
                Rotate(physics_group, angle=PI, axis=OUT),
                run_time=2
            )
            self.wait(1)
            
            # 5. Clone / Copy
            # Create a copy of water and put it in the center
            water_copy = water.copy()
            # Change color to distinguish
            for m in water_copy.atoms_group:
                 if hasattr(m, "set_color"): m.set_color(BLUE)
            
            self.play(
                TransformFromCopy(water, water_copy),
                water_copy.animate.move_to(DOWN * 2).scale(0.8)
            )
            self.wait(2)

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

