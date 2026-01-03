#!/usr/bin/env python3
"""
Chemanim Setup CLI - Interactive dependency installer.

Run after installing chemanim to add optional dependencies:
    chemanim-setup
"""

import subprocess
import sys


def main():
    """Interactive setup for chemanim optional dependencies."""
    print("\n" + "=" * 60)
    print("  🧪 Chemanim Setup - Optional Dependencies Installer")
    print("=" * 60)
    print("\nChemanim core is installed. Choose additional features:\n")
    
    options = {
        "1": {
            "name": "All Features (Recommended)",
            "desc": "ManimGL + Biotite + RDKit + ChemPy + ChemFormula + py3Dmol",
            "packages": ["manimgl", "biotite", "py3Dmol", "rdkit", "chempy", "chemformula"],
            "extra": "all"
        },
        "2": {
            "name": "Animations Only",
            "desc": "ManimGL for creating chemistry animations",
            "packages": ["manimgl"],
            "extra": "vis"
        },
        "3": {
            "name": "Chemistry Analysis",
            "desc": "RDKit + ChemPy + ChemFormula for molecular analysis",
            "packages": ["rdkit", "chempy", "chemformula"],
            "extra": "chem"
        },
        "4": {
            "name": "Protein Analysis",
            "desc": "Biotite for secondary structure detection",
            "packages": ["biotite"],
            "extra": "bio"
        },
        "5": {
            "name": "3D Viewer",
            "desc": "py3Dmol for interactive 3D molecule viewing",
            "packages": ["py3Dmol"],
            "extra": "viewer"
        },
        "6": {
            "name": "Skip",
            "desc": "Use core features only (can run this again later)",
            "packages": [],
            "extra": None
        }
    }
    
    # Display options
    for key, opt in options.items():
        rec = " ⭐" if key == "1" else ""
        print(f"  [{key}] {opt['name']}{rec}")
        print(f"      {opt['desc']}\n")
    
    # Get user choice
    while True:
        choice = input("Enter your choice (1-6) [1]: ").strip() or "1"
        if choice in options:
            break
        print("Invalid choice. Please enter 1-6.")
    
    selected = options[choice]
    
    if not selected["packages"]:
        print("\n✓ Setup complete! Using core features only.")
        print("  Run 'chemanim-setup' anytime to add more features.\n")
        return 0
    
    print(f"\n📦 Installing: {', '.join(selected['packages'])}...")
    print("-" * 40)
    
    try:
        # Install the selected packages
        cmd = [sys.executable, "-m", "pip", "install"] + selected["packages"]
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print(f"  ✅ Successfully installed {selected['name']}!")
        print("=" * 60)
        print("\nYou're ready to go! Try these examples:")
        
        if "manimgl" in selected["packages"]:
            print("  • manimgl examples/demo_reaction.py")
        if "rdkit" in selected["packages"]:
            print("  • RDKit molecular analysis enabled")
        if "chempy" in selected["packages"]:
            print("  • ChemPy chemical equations enabled")
        if "chemformula" in selected["packages"]:
            print("  • ChemFormula parsing enabled")
        if "biotite" in selected["packages"]:
            print("  • Protein secondary structure analysis enabled")
        if "py3Dmol" in selected["packages"]:
            print("  • python -c \"from chemanim.viewer_3d import show_py3dmol\"")
        
        print()
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed with error code {e.returncode}")
        print("Try installing manually:")
        print(f"  pip install chemanim[{selected['extra']}]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
