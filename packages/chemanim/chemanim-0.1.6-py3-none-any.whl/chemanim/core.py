"""Core molecule classes for Chemanim.

MIGRATED TO MANIMGL (from Manim Community Edition)
"""

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    # Dummy classes to allow code to run without ManimGL
    class VGroup:
        def __init__(self, **kwargs): pass
        def add(self, *args): pass
        def move_to(self, *args): return self
        def shift(self, *args): return self
        def scale(self, *args): return self
        def rotate(self, *args, **kwargs): return self
        def set_z_index(self, *args): return self
        def copy(self): return self
        def get_center(self): return np.array([0,0,0])
        def add_updater(self, *args): pass
        def remove_updater(self, *args): pass
        def put_start_and_end_on(self, *args): pass
    class VMobject(VGroup): pass
    class Line(VGroup):
        def __init__(self, *args, **kwargs): pass
    class Circle(VGroup):
         def __init__(self, *args, **kwargs): pass
         def get_center(self): return np.array([0,0,0])
    class Text(VGroup):
        def __init__(self, *args, **kwargs): pass
        def move_to(self, *args): pass
    class Scene:
        def construct(self): pass
    
    # Simple color stubs
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GREY = "#888888"

from collections import Counter

from .data import get_element_data
import numpy as np

class Atom(VGroup):
    def __init__(self, element, **kwargs):
        super().__init__(**kwargs)
        self.element_data = get_element_data(element)
        if not self.element_data:
             # Default fallback
             self.element_data = {"symbol": str(element), "color": "#FFFFFF", "radius": 0.5}
        
        self.color = self.element_data["color"]
        self.radius = self.element_data.get("radius", 0.5) * 0.5 # Scale down a bit for visualization
        self.symbol = self.element_data["symbol"]

        self.nucleus = Circle(radius=self.radius, color=self.color, fill_opacity=1, stroke_color=WHITE, stroke_width=2)
        self.text = Text(self.symbol, font_size=24, color=BLACK if self._is_bright(self.color) else WHITE)
        self.text.move_to(self.nucleus.get_center())

        self.add(self.nucleus, self.text)

    def _is_bright(self, hex_color):
        if not MANIM_AVAILABLE:
            return True # Default to black text on white bg usually
        # customized brightness check
        try:
            # ManimGL color handling
            h = hex_color.lstrip("#")
            if len(h) == 3:
                h = "".join([c * 2 for c in h])
            r, g, b = tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
            return (r*0.299 + g*0.587 + b*0.114) > 0.7
        except:
             return True

    @property
    def center_point(self):
        return self.nucleus.get_center()

class Bond(Line):
    def __init__(self, atom1, atom2, bond_type=1, **kwargs):
        self.atom1 = atom1
        self.atom2 = atom2
        self.bond_type = bond_type
        super().__init__(atom1.get_center(), atom2.get_center(), color=GREY, stroke_width=4, **kwargs)
        self.add_updater(lambda m: m.put_start_and_end_on(self.atom1.get_center(), self.atom2.get_center()))
        self.set_z_index(-1) # Bonds behind atoms

class Molecule(VGroup):
    def __init__(self, atoms=None, bonds=None, **kwargs):
        super().__init__(**kwargs)
        self.atoms = atoms if atoms else []
        self.bonds = bonds if bonds else []
        self.dimensionality = None
        self.add(*self.bonds, *self.atoms)

    def add_atom(self, atom):
        self.atoms.append(atom)
        self.add(atom)

    def add_bond(self, bond):
        self.bonds.append(bond)
        self.add(bond)
        # Ensure bond is behind atoms visual wise
        bond.set_z_index(-1)

    @classmethod
    def from_pubchem(cls, identifier):
        from .connect import fetch_molecule_data
        
        data = fetch_molecule_data(identifier)
        if not data:
            raise ValueError(f"Could not fetch data for {identifier}")
        return cls._build_from_data(data)
    
    @classmethod
    def from_smiles_rdkit(cls, smiles, add_h=False, dimensionality="2d", **builder_kwargs):
        """
        Build a Molecule using RDKit for coordinate generation.
        Requires the optional rdkit dependency.
        """
        from .rdkit_adapter import molecule_data_from_smiles

        data = molecule_data_from_smiles(
            smiles,
            add_h=add_h,
            dimensionality=dimensionality,
            **builder_kwargs,
        )
        return cls._build_from_data(data)
    
    @classmethod
    def from_file(cls, filepath):
        import json
        from .connect import parse_pubchem_json
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        parsed_data = parse_pubchem_json(data)
        if not parsed_data:
             raise ValueError(f"Could not parse data from {filepath}")
             
        return cls._build_from_data(parsed_data)

    @classmethod
    def _build_from_data(cls, data):
        atoms_data = data['atoms']
        bonds_data = data['bonds']
        coords_list = data.get('coords', [])
        if atoms_data and all('coords' in a for a in atoms_data):
            coords = np.array([a['coords'] for a in atoms_data], dtype=float)
        elif coords_list:
            coords = np.array(coords_list, dtype=float)
        else:
            coords = np.empty((0, 3))

        molecule = cls()
        created_atoms = []

        # Center coordinates
        if coords.size:
            if coords.shape[1] == 2:
                zeros = np.zeros((coords.shape[0], 1))
                coords = np.concatenate([coords, zeros], axis=1)
            mean_coord = np.mean(coords, axis=0) 
            coords = coords - mean_coord
            dimensionality = 3 if np.any(np.abs(coords[:,2]) > 1e-6) else 2
        else:
            dimensionality = data.get('dimensionality', 2)
        
        for i, atom_info in enumerate(atoms_data):
            atom = Atom(atom_info['element'])
            if len(coords) > i:
                 pos = coords[i]
                 atom.move_to(pos * 2) # Scale up slightly for visibility
            created_atoms.append(atom)
            molecule.add_atom(atom)

        for bond_info in bonds_data:
            a1_idx = bond_info['aid1'] - 1 
            a2_idx = bond_info['aid2'] - 1
            if 0 <= a1_idx < len(created_atoms) and 0 <= a2_idx < len(created_atoms):
                bond = Bond(created_atoms[a1_idx], created_atoms[a2_idx], bond_type=bond_info['order'])
                molecule.add_bond(bond)
                
        molecule.dimensionality = dimensionality
        return molecule

    def composition(self):
        """
        Return a dict mapping element symbols to counts.
        """
        counts = Counter()
        for atom in self.atoms:
            symbol = getattr(atom, "symbol", None)
            if not symbol:
                element_data = getattr(atom, "element_data", None)
                if element_data:
                    symbol = element_data.get("symbol")
            if not symbol:
                continue
            counts[symbol] += 1
        return dict(counts)

    def molecular_formula(self, hill=True, include_hydrogens=True):
        """
        Return the molecular formula string (Hill notation by default).
        """
        counts = Counter(self.composition())
        if not include_hydrogens:
            counts.pop("H", None)
        if not counts:
            return ""

        def fmt(symbol, count):
            return f"{symbol}{count if count > 1 else ''}"

        pieces = []
        working = dict(counts)

        if hill:
            if "C" in working:
                pieces.append(fmt("C", working.pop("C")))
                if "H" in working:
                    pieces.append(fmt("H", working.pop("H")))
            for symbol in sorted(working):
                pieces.append(fmt(symbol, working[symbol]))
        else:
            for symbol in sorted(working):
                pieces.append(fmt(symbol, working[symbol]))

        return "".join(pieces)

    def molecular_weight(self):
        """
        Return the approximate molecular weight (g/mol) using periodic table data.
        """
        total = 0.0
        for atom in self.atoms:
            element_data = getattr(atom, "element_data", None) or {}
            mass = element_data.get("mass")
            if mass is None:
                continue
            total += float(mass)
        return total
