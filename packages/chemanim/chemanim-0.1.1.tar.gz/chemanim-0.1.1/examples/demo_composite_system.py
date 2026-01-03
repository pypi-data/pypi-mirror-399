"""Demo transforming multiple molecules as a single composite object.

This shows how to group multiple ChemObject3D instances into one VGroup
and manipulate them together (rotate, scale, shift) as if they were one large object.
"""

from manimlib import *
from chemanim.chem_object_3d import ChemObject3D, RenderStyle


class CompositeSystemDemo(Scene):  # ManimGL
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=2.0)
        
        # 1. Create individual molecules
        # Ethanol
        ethanol = ChemObject3D.from_smiles_rdkit("CCO", add_h=True)
        ethanol.shift(LEFT * 2)
        
        # Water
        water = ChemObject3D.from_smiles_rdkit("O", add_h=True)
        water.shift(RIGHT * 2)
        
        # Carbon Dioxide
        co2 = ChemObject3D.from_smiles_rdkit("O=C=O", add_h=False) # No implicit H for CO2 if distinct
        co2.shift(UP * 2)
        
        # 2. Group them into a single "composite" VGroup
        molecular_system = VGroup(ethanol, water, co2)
        
        # Add the whole system to scene
        self.add(molecular_system)
        
        # Label
        label = Text("Composite Rotation", font_size=36)
        self.add_fixed_in_frame_mobjects(label)
        label.to_edge(UP)
        
        self.wait(1)
        
        # 3. Transform the ENTIRE system as one object (Rotation)
        self.play(
            Rotate(molecular_system, angle=PI, axis=UP),
            run_time=3
        )
        
        # 4. Scale the ENTIRE system
        self.play(
            molecular_system.animate.scale(0.5),
            run_time=1.5
        )
        
        # 5. Move the ENTIRE system
        self.play(
            molecular_system.animate.shift(LEFT * 1 + DOWN * 1),
            run_time=1.5
        )
        
        self.wait(1)
        
        # 6. Apply render style to all children recursively (custom helper needed or simple loop)
        # Note: ChemObject3D has apply_render_style, but VGroup doesn't.
        # We can iterate:
        label.become(Text("Apply Render Style to All", font_size=36))
        label.to_edge(UP)
        
        rect = SurroundingRectangle(label, color=BLUE, buff=0.2)
        self.add_fixed_in_frame_mobjects(rect)
        
        self.wait(0.5)
        
        # Apply 'Spheres' style to all molecules in the system
        # Since we want to animate or update them, we just call the method
        for mol in molecular_system:
            if isinstance(mol, ChemObject3D):
                mol.apply_render_style(RenderStyle.SPHERES)
        
        self.wait(2)
        
        # Rotate again to show they are still a group
        self.play(
            Rotate(molecular_system, angle=PI, axis=RIGHT),
            run_time=2
        )
        
        self.wait(2)
