"""Optional RDKit adapter to build ChemObject-compatible data and annotations."""

from typing import Dict, Any, List, Tuple


def _require_rdkit():
    try:
        from rdkit import Chem  # noqa: F401
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "RDKit is required for RDKit-backed builders. "
            "Install with `pip install rdkit-pypi` (manylinux/mac) or use conda-forge on Windows."
        ) from exc


def _prepare_mol(smiles: str, add_h: bool, existing=None):
    """Create (or reuse) an RDKit Mol with optional explicit hydrogens."""
    _require_rdkit()
    from rdkit import Chem

    if existing is not None:
        mol = existing
    else:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Could not parse SMILES: {smiles}")
    if add_h:
        mol = Chem.AddHs(mol)
    return mol


def _coords_from_conformer(conf) -> List[List[float]]:
    coords: List[List[float]] = []
    for idx in range(conf.GetNumAtoms()):
        pos = conf.GetAtomPosition(idx)
        coords.append([pos.x, pos.y, pos.z])
    return coords


def _atoms_and_bonds_from_mol(mol, coords: List[List[float]]):
    atoms: List[Dict[str, Any]] = []
    for idx, atom in enumerate(mol.GetAtoms()):
        atom_coords = coords[idx] if idx < len(coords) else [0.0, 0.0, 0.0]
        atoms.append({
            "element": atom.GetSymbol(),
            "coords": atom_coords,
        })

    bonds: List[Dict[str, Any]] = []
    for bond in mol.GetBonds():
        order = int(bond.GetBondTypeAsDouble())
        bonds.append({
            "aid1": bond.GetBeginAtomIdx() + 1,
            "aid2": bond.GetEndAtomIdx() + 1,
            "order": order,
        })
    return atoms, bonds


def molecule_data_from_smiles(
    smiles: str,
    add_h: bool = False,
    dimensionality: str = "2d",
    optimize_3d: bool = True,
    random_seed: int = 0,
) -> Dict[str, Any]:
    """Convert SMILES to the molecule_data dict expected by ChemObject.

    Set ``dimensionality`` to ``"3d"`` to embed a 3D conformer instead of 2D coords.
    """
    _require_rdkit()
    from rdkit.Chem import AllChem

    use_3d = str(dimensionality).lower().startswith("3")
    mol = _prepare_mol(smiles, add_h=add_h)

    if use_3d:
        coords, symbols, mol = compute_rdkit_3d_coords(
            smiles,
            add_h=add_h,
            optimize=optimize_3d,
            random_seed=random_seed,
            _prepared_mol=mol,
        )
        dim_flag = 3
    else:
        AllChem.Compute2DCoords(mol)
        conf = mol.GetConformer()
        coords = _coords_from_conformer(conf)
        coords = [[x, y, 0.0] for x, y, _ in coords]
        dim_flag = 2

    atoms, bonds = _atoms_and_bonds_from_mol(mol, coords)

    return {
        "atoms": atoms,
        "bonds": bonds,
        "smiles": smiles,
        "dimensionality": dim_flag,
    }


def compute_rdkit_2d_coords(smiles: str, add_h: bool = False) -> Tuple[List[List[float]], List[str]]:
    """Compute 2D coordinates via RDKit's Compute2DCoords.

    Returns (coords, symbols) where coords are [x, y, 0.0] per atom in RDKit order.
    """
    _require_rdkit()
    from rdkit.Chem import AllChem

    mol = _prepare_mol(smiles, add_h=add_h)
    AllChem.Compute2DCoords(mol)
    conf = mol.GetConformer()
    coords = _coords_from_conformer(conf)
    coords = [[x, y, 0.0] for x, y, _ in coords]
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]
    return coords, symbols


def compute_rdkit_3d_coords(
    smiles: str,
    add_h: bool = False,
    optimize: bool = True,
    random_seed: int = 0,
    _prepared_mol=None,
) -> Tuple[List[List[float]], List[str], Any]:
    """Compute 3D coordinates via RDKit's ETKDG embedder.

    Returns (coords, symbols, mol) where coords include XYZ in Angstrom units.
    """
    _require_rdkit()
    from rdkit.Chem import AllChem

    mol = _prepare_mol(smiles, add_h=add_h, existing=_prepared_mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    status = AllChem.EmbedMolecule(mol, params)
    if status != 0:
        raise ValueError(f"RDKit could not embed a 3D conformer for: {smiles}")

    if optimize:
        try:
            AllChem.UFFOptimizeMolecule(mol)
        except Exception:
            pass  # Optional optimization; ignore failures

    conf = mol.GetConformer()
    coords = _coords_from_conformer(conf)
    symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]
    return coords, symbols, mol


# Functional groups aligned with the reference poster (hydrocarbons, halogens, O/N/S/P groups).
# Each entry holds a user-facing label, category (for coloring), and SMARTS pattern.
FUNCTIONAL_GROUP_DEFS: List[Dict[str, str]] = [
    {"key": "alkane", "label": "Alkane", "category": "hydrocarbon", "smarts": "[CX4;!$([CX4][O,N,S,F,Cl,Br,I])]"},
    {"key": "alkene", "label": "Alkene", "category": "hydrocarbon", "smarts": "C=C"},
    {"key": "alkyne", "label": "Alkyne", "category": "hydrocarbon", "smarts": "C#C"},
    {"key": "arene", "label": "Arene", "category": "hydrocarbon", "smarts": "a1aaaaa1"},
    {"key": "haloalkane", "label": "Haloalkane", "category": "halogen", "smarts": "[CX4][F,Cl,Br,I]"},
    {"key": "alcohol", "label": "Alcohol", "category": "oxygen", "smarts": "[CX4;!$(C=O)][OX2H]"},
    {"key": "aldehyde", "label": "Aldehyde", "category": "oxygen", "smarts": "[CX3H1](=O)[#6]"},
    {"key": "ketone", "label": "Ketone", "category": "oxygen", "smarts": "[CX3](=O)[#6][#6]"},
    {"key": "carboxylic_acid", "label": "Carboxylic acid", "category": "oxygen", "smarts": "C(=O)[OX2H1]"},
    {"key": "acid_anhydride", "label": "Acid anhydride", "category": "oxygen", "smarts": "C(=O)OC(=O)"},
    {"key": "acyl_halide", "label": "Acyl halide", "category": "halogen", "smarts": "[CX3](=O)[F,Cl,Br,I]"},
    {"key": "ester", "label": "Ester", "category": "oxygen", "smarts": "[CX3](=O)O[CX4]"},
    {"key": "ether", "label": "Ether", "category": "oxygen", "smarts": "[OD2]([#6])[#6]"},
    {"key": "epoxide", "label": "Epoxide", "category": "oxygen", "smarts": "[OX2]1[CH2][CH2]1"},
    {"key": "amine", "label": "Amine", "category": "nitrogen", "smarts": "[NX3;!$(NC=O)]"},
    {"key": "amide", "label": "Amide", "category": "nitrogen", "smarts": "[NX3][CX3](=O)"},
    {"key": "nitrate", "label": "Nitrate", "category": "nitrogen", "smarts": "[NX3](=O)([O-])[O-]"},
    {"key": "nitrite", "label": "Nitrite", "category": "nitrogen", "smarts": "[NX2]=[OX1-]"},
    {"key": "nitrile", "label": "Nitrile", "category": "nitrogen", "smarts": "C#N"},
    {"key": "nitro", "label": "Nitro", "category": "nitrogen", "smarts": "[NX3](=O)=O"},
    {"key": "nitroso", "label": "Nitroso", "category": "nitrogen", "smarts": "[NX2]=O"},
    {"key": "imine", "label": "Imine", "category": "nitrogen", "smarts": "[CX3]=[NX2]"},
    {"key": "imide", "label": "Imide", "category": "nitrogen", "smarts": "[CX3](=O)N[CX3](=O)"},
    {"key": "azide", "label": "Azide", "category": "nitrogen", "smarts": "N=[NX1-]=[NX2+]"},
    {"key": "cyanate", "label": "Cyanate", "category": "nitrogen", "smarts": "[OX2][CX2]#N"},
    {"key": "isocyanate", "label": "Isocyanate", "category": "nitrogen", "smarts": "[NX1]=[CX2]=[OX1]"},
    {"key": "azo", "label": "Azo compound", "category": "nitrogen", "smarts": "N=N"},
    {"key": "thiol", "label": "Thiol", "category": "sulfur", "smarts": "[SX2H]"},
    {"key": "sulfide", "label": "Sulfide", "category": "sulfur", "smarts": "[#16X2]([#6])[#6]"},
    {"key": "disulfide", "label": "Disulfide", "category": "sulfur", "smarts": "[#16X2]-[#16X2]"},
    {"key": "sulfoxide", "label": "Sulfoxide", "category": "sulfur", "smarts": "[#16X3+][OX1-]"},
    {"key": "sulfone", "label": "Sulfone", "category": "sulfur", "smarts": "[#16X4](=O)(=O)"},
    {"key": "sulfinic_acid", "label": "Sulfinic acid", "category": "sulfur", "smarts": "[#16X3](=O)[OX2H]"},
    {"key": "sulfonic_acid", "label": "Sulfonic acid", "category": "sulfur", "smarts": "[#16X4](=O)(=O)[OX2H]"},
    {"key": "sulfonate_ester", "label": "Sulfonate ester", "category": "sulfur", "smarts": "[#16X4](=O)(=O)O[CX4]"},
    {"key": "thiocyanate", "label": "Thiocyanate", "category": "sulfur", "smarts": "SC#N"},
    {"key": "isothiocyanate", "label": "Isothiocyanate", "category": "sulfur", "smarts": "N=C=S"},
    {"key": "thial", "label": "Thial", "category": "sulfur", "smarts": "[CX3H1]=[SX1]"},
    {"key": "thioketone", "label": "Thioketone", "category": "sulfur", "smarts": "[CX3](=[SX1])[#6]"},
    {"key": "phosphine", "label": "Phosphine", "category": "phosphorus", "smarts": "[PX3]"},
]


def functional_group_palette() -> Dict[str, str]:
    """Default color palette keyed by functional group category."""
    return {
        "hydrocarbon": "#555555",  # grey
        "halogen": "#7BB662",      # green
        "oxygen": "#D64545",       # red
        "nitrogen": "#4A90E2",     # blue
        "sulfur": "#D98C1F",       # orange/gold
        "phosphorus": "#7A59AC",   # purple
        "default": "#BBBBBB",
    }


def detect_functional_groups(smiles: str, add_h: bool = False) -> List[Dict[str, Any]]:
    """
    Detect functional groups via SMARTS matches using RDKit.

    Returns a list of dictionaries containing ``key``, ``label``, ``category``, and
    ``atom_indices`` (0-based RDKit indices).
    """
    _require_rdkit()
    from rdkit import Chem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Could not parse SMILES: {smiles}")
    if add_h:
        mol = Chem.AddHs(mol)

    results: List[Dict[str, Any]] = []
    for fg in FUNCTIONAL_GROUP_DEFS:
        patt = Chem.MolFromSmarts(fg["smarts"])
        if patt is None:
            continue
        matches = mol.GetSubstructMatches(patt)
        for match in matches:
            results.append({
                "key": fg["key"],
                "label": fg["label"],
                "category": fg["category"],
                "atom_indices": list(match),
            })
    return results
