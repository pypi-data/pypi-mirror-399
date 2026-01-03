"""ManimGL Demo: All 4 PubChem-style 3D render modes.

Render Styles:
1. Ball and Stick - Atoms as spheres connected by split-colored bonds
2. Sticks - Thick cylindrical bonds only (no visible atom spheres)
3. Wire-Frame - Thin lines for bonds with small dots at atoms
4. Space-Filling - Large overlapping spheres based on van der Waals radii

Run: manimgl examples/demo_render_styles.py RenderStylesDemo -w
"""

from manimlib import *
from chemanim.chem_object_3d import ChemObject3D, RenderStyle


class RenderStylesDemo(Scene):
    """Demo showing all 4 render styles with ethanol molecule side-by-side."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=-45 * DEGREES, phi=60 * DEGREES)
        frame.scale(0.4)  # Zoom in
        
        # Create 4 molecules with different render styles
        styles = [
            ("Ball and Stick", RenderStyle.BALL_AND_STICK),
            ("Sticks", RenderStyle.STICKS),
            ("Wire-Frame", RenderStyle.WIRE_FRAME),
            ("Space-Filling", RenderStyle.SPACE_FILLING),
        ]
        
        molecules = []
        labels = []
        
        positions = [
            np.array([-3.5, 1.8, 0]),   # Top-left
            np.array([3.5, 1.8, 0]),    # Top-right
            np.array([-3.5, -1.8, 0]),  # Bottom-left
            np.array([3.5, -1.8, 0]),   # Bottom-right
        ]
        
        for i, (name, style) in enumerate(styles):
            mol = ChemObject3D.from_smiles_rdkit(
                "CCO",  # Ethanol (same as PubChem example)
                add_h=True,
                show_labels=False,
                render_style=style,
            ).enable_dynamic_bonds()
            
            mol.move_to(positions[i])
            molecules.append(mol)
            
            # Create label for each style
            label = Text(name, font_size=24, color=WHITE)
            label.move_to(positions[i] + np.array([0, -1.2, 0]))
            label.fix_in_frame()
            labels.append(label)
        
        # Add all molecules and labels
        for mol, label in zip(molecules, labels):
            self.add(mol, label)
        
        self.wait(1)
        
        # Rotate all molecules together
        self.play(
            *[Rotate(mol, angle=PI, axis=UP) for mol in molecules],
            run_time=3
        )
        
        self.play(
            *[Rotate(mol, angle=PI/2, axis=RIGHT) for mol in molecules],
            run_time=2
        )
        
        self.wait(2)


class BaseSingleStyleDemo(Scene):
    """Base class for single style demos."""
    STYLE = RenderStyle.BALL_AND_STICK
    NAME = "Ball and Stick"

    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=-45 * DEGREES, phi=60 * DEGREES)
        
        mol = ChemObject3D.from_smiles_rdkit(
            "CCO",  # Ethanol
            add_h=True,
            show_labels=False,
            render_style=self.STYLE,
        ).enable_dynamic_bonds()
        
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Rotate to a nice viewing angle
        self.play(Rotate(mol, angle=45*DEGREES, axis=UP), run_time=0.5)
        self.play(Rotate(mol, angle=30*DEGREES, axis=RIGHT), run_time=0.5)


class DemoBallAndStick(BaseSingleStyleDemo):
    STYLE = RenderStyle.BALL_AND_STICK
    NAME = "Ball and Stick"

class DemoSticks(BaseSingleStyleDemo):
    STYLE = RenderStyle.STICKS
    NAME = "Sticks"

class DemoWireFrame(BaseSingleStyleDemo):
    STYLE = RenderStyle.WIRE_FRAME
    NAME = "Wire-Frame"

class DemoSpaceFilling(BaseSingleStyleDemo):
    STYLE = RenderStyle.SPACE_FILLING
    NAME = "Space-Filling"

class DemoSpheres(BaseSingleStyleDemo):
    STYLE = RenderStyle.SPHERES
    NAME = "Spheres"


class SingleStyleDemo(Scene):
    """Demo to test a single render style (legacy)."""
    
    # Change this to test different styles
    STYLE = RenderStyle.BALL_AND_STICK
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=-45 * DEGREES, phi=60 * DEGREES)
        frame.scale(0.45)
        
        mol = ChemObject3D.from_smiles_rdkit(
            "CCO",  # Ethanol
            add_h=True,
            show_labels=True,
            render_style=self.STYLE,
        ).enable_dynamic_bonds()
        
        mol.enable_label_billboarding(self.camera)
        mol.move_to(ORIGIN)
        self.add(mol)
        
        # Smooth rotation
        self.play(Rotate(mol, angle=PI, axis=UP), run_time=3)
        self.play(Rotate(mol, angle=PI/2, axis=RIGHT), run_time=2)
        self.wait(1)


class StyleTransitionDemo(Scene):
    """Demo showing animated transition between render styles."""
    
    def construct(self):
        # ManimGL: Use frame for camera control
        frame = self.camera.frame
        frame.set_euler_angles(theta=-45 * DEGREES, phi=60 * DEGREES)
        frame.scale(0.45)
        
        # Start with ball_and_stick
        mol = ChemObject3D.from_smiles_rdkit(
            "CCO",
            add_h=True,
            show_labels=False,
            render_style=RenderStyle.BALL_AND_STICK,
        ).enable_dynamic_bonds()
        
        mol.move_to(ORIGIN)
        self.add(mol)
        
        style_label = Text("Ball and Stick", font_size=32, color=WHITE)
        style_label.fix_in_frame()
        style_label.to_edge(UP)
        self.add(style_label)
        
        self.wait(1)
        self.play(Rotate(mol, angle=PI/2, axis=UP), run_time=1.5)
        
        # Transition to Sticks
        self.play(FadeOut(style_label))
        mol.apply_render_style(RenderStyle.STICKS)
        style_label = Text("Sticks", font_size=32, color=WHITE)
        style_label.fix_in_frame()
        style_label.to_edge(UP)
        self.add(style_label)
        self.wait(0.5)
        self.play(Rotate(mol, angle=PI/2, axis=UP), run_time=1.5)
        
        # Transition to Wire-Frame
        self.play(FadeOut(style_label))
        mol.apply_render_style(RenderStyle.WIRE_FRAME)
        style_label = Text("Wire-Frame", font_size=32, color=WHITE)
        style_label.fix_in_frame()
        style_label.to_edge(UP)
        self.add(style_label)
        self.wait(0.5)
        self.play(Rotate(mol, angle=PI/2, axis=UP), run_time=1.5)
        
        # Transition to Space-Filling
        self.play(FadeOut(style_label))
        mol.apply_render_style(RenderStyle.SPACE_FILLING)
        style_label = Text("Space-Filling", font_size=32, color=WHITE)
        style_label.fix_in_frame()
        style_label.to_edge(UP)
        self.add(style_label)
        self.wait(0.5)
        self.play(Rotate(mol, angle=PI/2, axis=UP), run_time=1.5)
        
        self.wait(2)


# Run commands (ManimGL):
# manimgl examples/demo_render_styles.py RenderStylesDemo -w
# manimgl examples/demo_render_styles.py DemoBallAndStick -w
# manimgl examples/demo_render_styles.py DemoSticks -w
# manimgl examples/demo_render_styles.py DemoWireFrame -w
# manimgl examples/demo_render_styles.py DemoSpaceFilling -w
