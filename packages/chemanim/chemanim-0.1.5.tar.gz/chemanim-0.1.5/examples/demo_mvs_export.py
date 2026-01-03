"""Test MolViewSpec integration via normal package import."""

import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath("src"))

try:
    from chemanim import MVSScene, check_mvs_available
except ImportError as e:
    print(f"Failed to import chemanim package: {e}")
    sys.exit(1)

print(f"MVS Available: {check_mvs_available()}")

if not check_mvs_available():
    print("Skipping MVS tests as molviewspec is not installed.")
    sys.exit(0)

print("\nCreating MVS Scene...")
scene = MVSScene()
scene.load_structure("1CRN")
scene.style_cartoon()
scene.color_by_chain()

# Add a specific component
scene.add_component(
    selector="ligand", 
    representation="ball_and_stick", 
    color="green", 
    label="My Ligand"
)

# Export MVSJ
json_output = scene.to_mvsj()
print(f"\nGenerated MVSJ ({len(json_output)} chars):")
print(json_output[:500] + "..." if len(json_output) > 500 else json_output)

# Verify some content
assert "1CRN" in json_output
assert "cartoon" in json_output
assert "ligand" in json_output
assert "ball_and_stick" in json_output
assert "green" in json_output

print("\n✓ Validated MVSJ content structure.")

# Try saving
output_file = "test_scene.mvsj"
scene.save_mvsj(output_file)
if os.path.exists(output_file):
    print(f"✓ File saved to {output_file}")
    # os.remove(output_file) # Keep it for inspection if needed

print("\nTest Complete!")
