import sys

def check_setup():
    print("Checking Chemanim Setup...")
    
    # Check Chemanim
    try:
        import chemanim
        print("[OK] chemanim imported successfully.")
    except ImportError as e:
        print(f"[FAIL] Could not import chemanim: {e}")
        return

    # Check Core Logic
    try:
        from chemanim.core import Atom
        print("[OK] chemanim.core imported.")
    except ImportError as e:
        print(f"[FAIL] Could not import chemanim.core: {e}")

    # Check PubChem
    try:
        import pubchempy
        print("[OK] pubchempy is installed.")
    except ImportError:
        print("[FAIL] pubchempy is missing.")

    # Check Biopython
    try:
        import Bio
        print("[OK] biopython is installed.")
    except ImportError:
        print("[FAIL] biopython is missing.")

    # Check Manim (Optional)
    try:
        import manim
        print("[OK] manim is installed. Animations should work.")
    except ImportError:
        print("[WARNING] manim is NOT installed or not working.")
        print("          Visual animations will not run, but you can still use the library for data/logic.")
        print("          To install manim, please see: https://docs.manim.community/en/stable/installation.html")

if __name__ == "__main__":
    check_setup()
