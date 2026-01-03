"""
Test file to evaluate ManimGL compatibility with Chemanim's 3D rendering.

KEY DIFFERENCES FROM MANIM CE:
1. Use `Group` instead of `VGroup` for 3D objects (Sphere, Cylinder, etc.)
2. Camera control via `self.camera.frame.set_euler_angles()`
3. Use `fix_in_frame()` instead of `add_fixed_in_frame_mobjects()`
4. No `ThreeDScene` class - just `Scene` with frame manipulation

Run with: manimgl examples/test_manimgl.py Test3DScene -w
"""

from manimlib import *
import numpy as np

print("✓ ManimGL imported successfully")


class TestBasic(Scene):
    """Simple 2D test scene for basic ManimGL compatibility."""
    
    def construct(self):
        title = Text("ManimGL Basic Test", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        circle = Circle(radius=1, color=RED)
        circle.move_to(LEFT * 2)
        
        square = Square(side_length=1.5, color=BLUE)
        square.move_to(RIGHT * 2)
        
        # VGroup works for 2D VMobjects
        group = VGroup(circle, square)
        
        self.play(FadeIn(group))
        self.play(Rotate(group, PI/2), run_time=2)
        
        success = Text("✓ Basic test passed!", font_size=36, color=GREEN)
        success.to_edge(DOWN)
        self.play(Write(success))
        self.wait(2)


class Test3DScene(Scene):
    """Test 3D scene with camera controls - ManimGL style.
    
    IMPORTANT: In ManimGL, 3D objects (Sphere, Cylinder, Surface) are NOT VMobjects.
    They are SurfaceMobjects. Use `Group` instead of `VGroup` for 3D objects!
    """
    
    def construct(self):
        # Set up 3D camera
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=30 * DEGREES,
            phi=75 * DEGREES,
        )
        
        title = Text("ManimGL 3D Test", font_size=36)
        title.fix_in_frame()
        title.to_edge(UP)
        self.add(title)
        
        # Create spheres - these are SurfaceMobjects, not VMobjects
        carbon = Sphere(radius=0.4, color=GREY_D)
        carbon.move_to(ORIGIN)
        
        hydrogen1 = Sphere(radius=0.25, color=WHITE)
        hydrogen1.move_to(UP * 1.2)
        
        hydrogen2 = Sphere(radius=0.25, color=WHITE)
        hydrogen2.move_to(DOWN * 0.6 + RIGHT * 1.0)
        
        hydrogen3 = Sphere(radius=0.25, color=WHITE)
        hydrogen3.move_to(DOWN * 0.6 + LEFT * 1.0)
        
        hydrogen4 = Sphere(radius=0.25, color=WHITE)
        hydrogen4.move_to(OUT * 0.8)
        
        # Use Group (not VGroup!) for 3D objects
        atoms = Group(carbon, hydrogen1, hydrogen2, hydrogen3, hydrogen4)
        
        self.play(FadeIn(atoms))
        self.wait(0.5)
        
        # Rotation animation
        self.play(Rotate(atoms, TAU, axis=UP), run_time=4)
        
        # Camera movement
        self.play(
            frame.animate.set_euler_angles(theta=-45 * DEGREES),
            run_time=2
        )
        
        self.wait(1)
        
        success = Text("✓ 3D Test Passed!", font_size=32, color=GREEN)
        success.fix_in_frame()
        success.to_edge(DOWN)
        self.play(FadeIn(success))
        self.wait(2)


class TestCylinder(Scene):
    """Test Cylinder rendering - critical for Chemanim bonds."""
    
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        
        title = Text("Cylinder Bond Test", font_size=36)
        title.fix_in_frame()
        title.to_edge(UP)
        self.add(title)
        
        try:
            # ManimGL Cylinder
            cyl = Cylinder(
                radius=0.1, 
                height=2.0,
                color=BLUE,
            )
            cyl.move_to(ORIGIN)
            
            self.play(FadeIn(cyl))
            self.wait(0.5)
            
            self.play(Rotate(cyl, PI/2, axis=RIGHT), run_time=1)
            
            success = Text("✓ Cylinder works!", font_size=32, color=GREEN)
            
        except Exception as e:
            print(f"Cylinder error: {e}")
            success = Text(f"✗ Cylinder failed", font_size=24, color=RED)
        
        success.fix_in_frame()
        success.to_edge(DOWN)
        self.play(FadeIn(success))
        self.wait(2)


class TestMoleculeWithBonds(Scene):
    """
    Test a complete molecule with atoms (spheres) and bonds (cylinders).
    This is the critical test for Chemanim compatibility.
    """
    
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        
        title = Text("Molecule with Bonds", font_size=32)
        title.fix_in_frame()
        title.to_edge(UP)
        self.add(title)
        
        # Atom positions (simple methane-like structure)
        c_pos = ORIGIN
        h_positions = [
            UP * 1.0,
            DOWN * 0.5 + RIGHT * 0.9,
            DOWN * 0.5 + LEFT * 0.9,
            OUT * 0.8,
        ]
        
        # Create atoms
        carbon = Sphere(radius=0.35, color=GREY_D)
        carbon.move_to(c_pos)
        
        hydrogens = Group()
        for pos in h_positions:
            h = Sphere(radius=0.2, color=WHITE)
            h.move_to(pos)
            hydrogens.add(h)
        
        # Create bonds using cylinders
        bonds = Group()
        for h_pos in h_positions:
            # Calculate bond vector
            bond_vec = h_pos - c_pos
            bond_length = np.linalg.norm(bond_vec)
            
            # Create cylinder
            bond = Cylinder(
                radius=0.06,
                height=bond_length * 0.6,  # Shorter than full distance
                color=GREY,
            )
            
            # Position at midpoint
            midpoint = (c_pos + h_pos) / 2
            bond.move_to(midpoint)
            
            # Rotate to align with bond direction
            # Default cylinder is along Z axis
            if bond_length > 0:
                bond_dir = bond_vec / bond_length
                # Rotation to align Z with bond_dir
                z_axis = np.array([0, 0, 1])
                if not np.allclose(bond_dir, z_axis):
                    rot_axis = np.cross(z_axis, bond_dir)
                    if np.linalg.norm(rot_axis) > 1e-6:
                        rot_axis = rot_axis / np.linalg.norm(rot_axis)
                        angle = np.arccos(np.clip(np.dot(z_axis, bond_dir), -1, 1))
                        bond.rotate(angle, axis=rot_axis)
            
            bonds.add(bond)
        
        # Combine all parts
        molecule = Group(bonds, carbon, hydrogens)
        
        self.play(FadeIn(molecule))
        self.wait(0.5)
        
        # Rotate molecule
        self.play(Rotate(molecule, TAU, axis=UP), run_time=4)
        
        # Move camera
        self.play(
            frame.animate.set_euler_angles(theta=-60 * DEGREES, phi=60 * DEGREES),
            run_time=2
        )
        
        self.wait(1)
        
        success = Text("✓ Full Molecule Rendering Works!", font_size=28, color=GREEN)
        success.fix_in_frame()
        success.to_edge(DOWN)
        self.play(FadeIn(success))
        self.wait(2)


class TestPerformance(Scene):
    """
    Performance test with multiple spheres.
    Compare rendering time with Manim CE.
    """
    
    def construct(self):
        import time
        
        frame = self.camera.frame
        frame.set_euler_angles(theta=30 * DEGREES, phi=70 * DEGREES)
        
        title = Text("Performance Test - 50 Spheres", font_size=32)
        title.fix_in_frame()
        title.to_edge(UP)
        self.add(title)
        
        # Create many spheres
        start = time.time()
        
        spheres = Group()
        for i in range(50):
            s = Sphere(radius=0.15, color=BLUE)
            # Random position
            pos = np.array([
                np.random.uniform(-4, 4),
                np.random.uniform(-2, 2),
                np.random.uniform(-1, 1),
            ])
            s.move_to(pos)
            spheres.add(s)
        
        creation_time = time.time() - start
        
        self.play(FadeIn(spheres), run_time=0.5)
        
        # Rotate all
        start = time.time()
        self.play(Rotate(spheres, PI, axis=UP), run_time=3)
        animation_time = time.time() - start
        
        info = Text(
            f"Creation: {creation_time:.2f}s\nAnimation: {animation_time:.2f}s",
            font_size=24
        )
        info.fix_in_frame()
        info.to_edge(DOWN)
        self.play(FadeIn(info))
        self.wait(2)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ManimGL Test Scenes Available:")
    print("="*60)
    print("  manimgl examples/test_manimgl.py TestBasic")
    print("  manimgl examples/test_manimgl.py Test3DScene")
    print("  manimgl examples/test_manimgl.py TestCylinder")
    print("  manimgl examples/test_manimgl.py TestMoleculeWithBonds")
    print("  manimgl examples/test_manimgl.py TestPerformance")
    print("\nFlags:")
    print("  -w      Write video file")
    print("  -l      Low quality (faster)")
    print("  -o      Open video after rendering")
    print("\nExample:")
    print("  manimgl examples/test_manimgl.py TestMoleculeWithBonds -w -l")
    print("="*60)
