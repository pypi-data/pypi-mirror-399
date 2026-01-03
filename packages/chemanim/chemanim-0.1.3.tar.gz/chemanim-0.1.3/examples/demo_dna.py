from manimlib import *
import numpy as np

class DnaStructureDemo(Scene):  # ManimGL
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        title = Text("DNA Synthesis & Structure", font_size=40)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # DNA Parameters
        height = 6
        radius = 1.5
        turns = 2
        base_pairs_per_turn = 10
        total_base_pairs = turns * base_pairs_per_turn
        
        # Colors
        COLOR_SUGAR_PHOSPHATE = GREY_B
        COLOR_A = RED_B
        COLOR_T = BLUE_B
        COLOR_C = GREEN_B
        COLOR_G = YELLOW_B
        
        # Lists to hold structure parts
        strand1_atoms = []
        strand2_atoms = []
        connections = []
        
        # Create the Double Helix
        for i in range(total_base_pairs):
            angle = i * (2 * PI / base_pairs_per_turn)
            z = -height/2 + i * (height / total_base_pairs)
            
            # Positions
            pos1 = np.array([radius * np.cos(angle), radius * np.sin(angle), z])
            pos2 = np.array([radius * np.cos(angle + PI + 0.5), radius * np.sin(angle + PI + 0.5), z]) # Offset 2nd strand slightly
            # Correct double helix offset is usually just PI (180 deg) + major/minor groove offset, but PI is fine for expanding
            pos2 = np.array([radius * np.cos(angle + PI), radius * np.sin(angle + PI), z])

            # Backbone Atoms (Simple Spheres)
            atom1 = Sphere(radius=0.2, color=COLOR_SUGAR_PHOSPHATE).move_to(pos1)
            atom2 = Sphere(radius=0.2, color=COLOR_SUGAR_PHOSPHATE).move_to(pos2)
            
            strand1_atoms.append(atom1)
            strand2_atoms.append(atom2)
            
            # Base Pairs (Cylinders or Lines connecting them)
            # A pairs with T, C pairs with G
            if i % 4 == 0:
                c1, c2 = COLOR_A, COLOR_T
            elif i % 4 == 1:
                c1, c2 = COLOR_C, COLOR_G
            elif i % 4 == 2:
                c1, c2 = COLOR_T, COLOR_A
            else:
                c1, c2 = COLOR_G, COLOR_C
            
            # Meet in the middle
            midpoint = (pos1 + pos2) / 2
            
            base1 = Cylinder(radius=0.1, height=np.linalg.norm(midpoint - pos1), color=c1)
            base1.rotate(angle, axis=OUT) # Roughly align? Cylinder rotation is tricky.
            # Easier approach: Line or Cylinder using put_start_and_end_on
            
            base1 = Cylinder(radius=0.08, height=1, color=c1)
            # Cylinder height is Z axis by default.
            # We want it from pos1 to midpoint
            # Manim's Cylinder is not easily defined by start/end points like Line.
            # Using Line for simplicity in wireframe or small radius Cylinder via rotation
            
            # Let's use thick Lines for "Synthesis" animation ease, or just Spheres for bases?
            # Let's use Line with stroke width. 
            # OR better: 3D Cylinder defined by geometry.
            
            # Let's use a composite object for the base pair
            # Left side
            bp1 = Line(start=pos1, end=midpoint, stroke_width=8, color=c1)
            # Right side
            bp2 = Line(start=pos2, end=midpoint, stroke_width=8, color=c2)
            
            connections.append(VGroup(bp1, bp2))

        # Animation: Synthesis (Growing from bottom up)
        
        # Group everything for rotation later
        molecule = VGroup()
        
        for i in range(len(strand1_atoms)):
            # Animate pair appearance
            self.play(
                FadeIn(strand1_atoms[i], shift=UP*0.5),
                FadeIn(strand2_atoms[i], shift=UP*0.5),
                Create(connections[i]),
                run_time=0.1
            )
            molecule.add(strand1_atoms[i], strand2_atoms[i], connections[i])
            
        self.wait(1)
        
        # 3D Rotation Preview
        self.play(Rotate(molecule, angle=2*PI, axis=Z_AXIS), run_time=5)
        self.wait()
        
        # Zoom out and rotate camera
        self.move_camera(phi=60 * DEGREES, theta=120 * DEGREES, zoom=0.8, run_time=3)
        self.wait()

