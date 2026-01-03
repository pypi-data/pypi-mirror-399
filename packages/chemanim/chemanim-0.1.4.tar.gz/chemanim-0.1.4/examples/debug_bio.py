from chemanim.bio import Macromolecule
import os

try:
    pdb_path = os.path.join("examples", "simple.pdb")
    print(f"Loading {pdb_path}...")
    mol = Macromolecule(pdb_path)
    print("Successfully loaded Macromolecule!")
    print(f"Number of atoms: {len(mol.molecule_data['atoms'])}")
    print(f"Number of bonds: {len(mol.molecule_data['bonds'])}")
    print("Sample atom:", mol.molecule_data['atoms'][0])
    if mol.molecule_data['bonds']:
        print("Sample bond:", mol.molecule_data['bonds'][0])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
