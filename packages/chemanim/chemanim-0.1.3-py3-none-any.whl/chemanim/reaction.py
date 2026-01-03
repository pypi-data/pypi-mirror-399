"""Chemical reaction animation module.

MIGRATED TO MANIMGL (from Manim Community Edition)
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    # Dummy classes for environments without ManimGL
    import numpy as np
    
    class VGroup:
        def __init__(self, *args, **kwargs): pass
        def add(self, *args): pass
        def arrange(self, *args, **kwargs): pass
        def move_to(self, *args): return self
    class Transform:
        def __init__(self, *args, **kwargs): pass
    class AnimationGroup:
        def __init__(self, *args, **kwargs): pass
    class FadeOut:
        def __init__(self, *args, **kwargs): pass
    class FadeIn:
        def __init__(self, *args, **kwargs): pass
    class Create:
        def __init__(self, *args, **kwargs): pass
    class Uncreate:
        def __init__(self, *args, **kwargs): pass
    class Wait:
        def __init__(self, *args, **kwargs): pass
    class Arrow(VGroup):
        def __init__(self, *args, **kwargs): pass
    class Scene:
        pass
    LEFT = np.array([-1, 0, 0])
    RIGHT = np.array([1, 0, 0])
    ORIGIN = np.array([0, 0, 0])

import numpy as np
from .core import Molecule, Atom, Bond
from .chem_object import ChemObject

class ChemicalReaction(VGroup):
    def __init__(self, reactants_ids, products_ids, use_chem_object=False, **kwargs):
        """
        reactants_ids: list of str or int (PubChem names or CIDs)
        products_ids: list of str or int
        use_chem_object: If True, uses 2D Line Structure (ChemObject). If False, uses Ball-and-Stick (Molecule).
        """
        super().__init__(**kwargs)
        self.use_chem_object = use_chem_object
        self.reactants_group = VGroup()
        self.products_group = VGroup()
        
        # 1. Fetch Reactants
        self.reactant_molecules = []
        for rid in reactants_ids:
            if use_chem_object:
                mol = ChemObject.from_pubchem(rid)
            else:
                mol = Molecule.from_pubchem(rid)
            self.reactant_molecules.append(mol)
            self.reactants_group.add(mol)
            
        # 2. Fetch Products
        self.product_molecules = []
        for pid in products_ids:
            if use_chem_object:
                mol = ChemObject.from_pubchem(pid)
            else:
                mol = Molecule.from_pubchem(pid)
            self.product_molecules.append(mol)
            self.products_group.add(mol)

        # 3. Layout (Initial)
        self.reactants_group.arrange(RIGHT, buff=1.0)
        self.products_group.arrange(RIGHT, buff=1.0)
        
        self.products_group.move_to(ORIGIN)
        self.reactants_group.move_to(ORIGIN)

        self.add(self.reactants_group)

        self.atom_mapping = self._map_atoms()

    def _map_atoms(self):
        """
        Greedy mapping by element type.
        Returns dict: {reactant_atom: product_atom}
        """
        def get_atoms(mol):
            if hasattr(mol, 'atoms'): return mol.atoms # Molecule class
            if hasattr(mol, 'atoms_group'): return list(mol.atoms_group) # ChemObject class
            return []
            
        def get_symbol(atom):
            # Prioritize explicit symbol attribute (added for stability)
            if hasattr(atom, 'symbol'): return atom.symbol
            if hasattr(atom, 'element_data'): return atom.element_data['symbol']
            # Fallback for Text objects
            return getattr(atom, 'text', str(atom))

        r_atoms_by_el = {}
        for mol in self.reactant_molecules:
            for atom in get_atoms(mol):
                el = get_symbol(atom)
                if el not in r_atoms_by_el: r_atoms_by_el[el] = []
                r_atoms_by_el[el].append(atom)
        
        p_atoms_by_el = {}
        for mol in self.product_molecules:
            for atom in get_atoms(mol):
                el = get_symbol(atom)
                if el not in p_atoms_by_el: p_atoms_by_el[el] = []
                p_atoms_by_el[el].append(atom)
        
        mapping = {}
        
        for el, r_atoms in r_atoms_by_el.items():
            if el in p_atoms_by_el:
                p_atoms = p_atoms_by_el[el]
                count = min(len(r_atoms), len(p_atoms))
                for i in range(count):
                    mapping[r_atoms[i]] = p_atoms[i]
                    
        return mapping

    def animate_reaction(self, run_time=2.0):
        """
        Returns an AnimationGroup for the reaction.
        """
        anims = []
        
        # 1. Handle Atoms (Movement)
        mapped_r_atoms = set()
        for r_atom, p_atom in self.atom_mapping.items():
            anims.append(Transform(r_atom, p_atom))
            mapped_r_atoms.add(r_atom)
        
        def get_atoms(mol):
            if hasattr(mol, 'atoms'): return mol.atoms
            if hasattr(mol, 'atoms_group'): return list(mol.atoms_group)
            return []

        # Reactant Fadeout
        for mol in self.reactant_molecules:
            for atom in get_atoms(mol):
                if atom not in mapped_r_atoms:
                    anims.append(FadeOut(atom))
        
        # Product Fadein
        mapped_p_atoms = set(self.atom_mapping.values())
        for mol in self.product_molecules:
            for atom in get_atoms(mol):
                if atom not in mapped_p_atoms:
                    atom.move_to(atom.get_center()) 
                    anims.append(FadeIn(atom))

        # 2. Handle Bonds
        def get_bonds(mol):
            if hasattr(mol, 'bonds'): return mol.bonds # Molecule
            if hasattr(mol, 'bonds_group'): return list(mol.bonds_group) # ChemObject
            return []
            
        r_bonds = []
        for mol in self.reactant_molecules:
            r_bonds.extend(get_bonds(mol))
            
        p_bonds = []
        for mol in self.product_molecules:
            p_bonds.extend(get_bonds(mol))

        if self.use_chem_object:
            # For Line Structures: FadeOut reactant bonds, FadeIn product bonds
            for b in r_bonds:
                anims.append(FadeOut(b))
            
            for b in p_bonds:
                anims.append(FadeIn(b))
        else:
            # Existing logic for Ball-and-Stick (Molecule class)
            self._animate_bonds_structure_mode(r_bonds, p_bonds, anims)

        print(f"DEBUG: Mapped {len(mapped_r_atoms)} atoms out of {len(list(self.atom_mapping.keys()))} possible.")
        
        # Filter out any None or empty animations
        anims = [a for a in anims if a is not None]
        
        if not anims:
            return Wait(run_time)
                
        return AnimationGroup(*anims, run_time=run_time)

    def _animate_bonds_structure_mode(self, r_bonds, p_bonds, anims):
        # Helper to find bond in products between two atoms
        def find_bond(atom_a, atom_b, bond_list):
            for b in bond_list:
                if (b.atom1 == atom_a and b.atom2 == atom_b) or \
                   (b.atom1 == atom_b and b.atom2 == atom_a):
                   return b
            return None

        matched_p_bonds = set()
        
        for r_bond in r_bonds:
            a1 = r_bond.atom1
            a2 = r_bond.atom2
            
            if a1 in self.atom_mapping and a2 in self.atom_mapping:
                target_a1 = self.atom_mapping[a1]
                target_a2 = self.atom_mapping[a2]
                target_bond = find_bond(target_a1, target_a2, p_bonds)
                
                if target_bond:
                    anims.append(Transform(r_bond, target_bond))
                    matched_p_bonds.add(target_bond)
                else:
                    anims.append(Uncreate(r_bond))
            else:
                anims.append(FadeOut(r_bond))

        for p_bond in p_bonds:
            if p_bond not in matched_p_bonds:
                anims.append(Create(p_bond))
