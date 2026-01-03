"""Demo: generate py3Dmol HTML and XYZ export for a small molecule.

Run:
    D:/Law/Chemanim/env311/Scripts/python.exe examples/demo_py3dmol_viewer.py

Requires optional dependency: pip install py3Dmol
"""

from pathlib import Path

from chemanim.connect import fetch_molecule_data
from chemanim.rdkit_adapter import molecule_data_from_smiles
from chemanim.viewer_3d import show_py3dmol, write_xyz


def build_molecule_data():
    # Prefer a deterministic SMILES->3D using RDKit if available; fallback to PubChem fetch.
    try:
        return molecule_data_from_smiles("CCO", add_h=True, dimensionality="3d")
    except Exception:
        data = fetch_molecule_data("ethanol")
        if not data:
            raise RuntimeError("Could not obtain molecule data via RDKit or PubChem")
        return data


def main():
    out_dir = Path("media/py3dmol")
    out_dir.mkdir(parents=True, exist_ok=True)

    mol = build_molecule_data()

    # Export XYZ for PyMOL or other tools
    xyz_path = write_xyz(out_dir / "ethanol.xyz", mol)
    print(f"XYZ written to {xyz_path}")

    # Build three styles and save as standalone HTML files
    styles = ["ball_and_stick", "stick", "ball"]
    for style in styles:
        try:
            view = show_py3dmol(mol, style=style, width=640, height=480)
            html_path = out_dir / f"ethanol_{style}.html"
            view.write_html(str(html_path))
            print(f"py3Dmol {style} written to {html_path}")
        except ImportError as exc:
            print(f"py3Dmol not installed; skipping {style} HTML. {exc}")


if __name__ == "__main__":
    main()
