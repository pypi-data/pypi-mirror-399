"""Optional chempy adapter to parse reactions and map species to ChemObject data."""
from typing import Dict, Any, List, Tuple


def _require_chempy():
    try:
        import chempy  # noqa: F401
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "chempy is required for reaction parsing. Install with `pip install chempy`."
        ) from exc


def parse_reaction_equation(equation: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Parse a reaction string (e.g., "H2 + O2 -> H2O") using chempy.

    Returns:
        (reactants, products) where each is a dict: species -> coefficient (float)
    """
    _require_chempy()
    from chempy.util.parsing import ReactionParser

    parser = ReactionParser()
    rxn = parser.parse_reaction(equation)
    return rxn.reactants, rxn.products


def build_reaction_chemobjects(
    equation: str,
    species_to_smiles: Dict[str, str],
    chemobject_kwargs: Dict[str, Any] | None = None,
    add_h: bool = True,
) -> Tuple[List[Tuple[str, Any]], List[Tuple[str, Any]]]:
    """
    Convert a reaction equation into ChemObject instances using RDKit layouts.

    Args:
        equation: reaction string, e.g., "H2 + O2 -> H2O".
        species_to_smiles: mapping from species name (matching the equation tokens) to SMILES.
        chemobject_kwargs: extra kwargs passed to ChemObject.from_smiles_rdkit (e.g., skeletal=True).
        add_h: whether to tell RDKit to add hydrogens for visualization.

    Returns:
        (reactants, products) lists of (label, chem_object)
    """
    from .rdkit_adapter import molecule_data_from_smiles
    from .chem_object import ChemObject

    chemobject_kwargs = chemobject_kwargs or {}
    reactants_map, products_map = parse_reaction_equation(equation)

    def make_side(side_map):
        out = []
        for species, coeff in side_map.items():
            smiles = species_to_smiles.get(species)
            if not smiles:
                raise ValueError(f"No SMILES provided for species '{species}'")
            data = molecule_data_from_smiles(smiles, add_h=add_h)
            mol = ChemObject(data, **chemobject_kwargs)
            label = f"{coeff:g} {species}" if coeff != 1 else species
            out.append((label, mol))
        return out

    return make_side(reactants_map), make_side(products_map)
