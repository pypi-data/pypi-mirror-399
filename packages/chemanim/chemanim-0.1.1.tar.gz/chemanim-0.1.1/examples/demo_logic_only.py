from chemanim.core import Molecule

def run_logic_demo():
    print("--- Chemanim Logic Demo (No Animation) ---")
    
    print("\n1. Creating an Atom manually...")
    # This import works even without Manim due to our dummy classes
    from chemanim.core import Atom
    h = Atom(1)
    print(f"Created Atom: {h.symbol} (Atomic Number: 1)")

    print("\n2. Fetching Molecule from PubChem...")
    try:
        mol_name = "aspirin"
        print(f"Fetching '{mol_name}'...")
        aspirin = Molecule.from_pubchem(mol_name)
        
        print(f"Successfully fetched {mol_name}!")
        print(f"Number of Atoms: {len(aspirin.atoms)}")
        print(f"Number of Bonds: {len(aspirin.bonds)}")
        
        # Verify composition
        elements = {}
        for atom in aspirin.atoms:
            s = atom.symbol
            elements[s] = elements.get(s, 0) + 1
        print(f"Composition: {elements}")
        
        print(f"Formula: {aspirin.molecular_formula()}")
        print(f"Molar Mass: {aspirin.molecular_weight():.2f} g/mol")
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Make sure you have an internet connection.")

    print("\n3. Building a molecule from SMILES via RDKit (optional)...")
    try:
        ethanol = Molecule.from_smiles_rdkit("CCO", dimensionality="3d", add_h=True)
        print("SMILES -> Molecule succeeded (requires RDKit).")
        print(f"Ethanol formula: {ethanol.molecular_formula()}")
        print(f"Ethanol weight: {ethanol.molecular_weight():.2f} g/mol")
    except ImportError as e:
        print(f"RDKit not installed: {e}")
    except Exception as e:
        print(f"Could not build from SMILES: {e}")

    print("\n--- Demo Completed ---")

if __name__ == "__main__":
    run_logic_demo()
