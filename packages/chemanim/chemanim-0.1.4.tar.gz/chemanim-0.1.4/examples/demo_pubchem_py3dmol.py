"""Fetch a molecule from PubChem and render an interactive 3D view with py3Dmol.

Usage:
    D:/Law/Chemanim/env311/Scripts/python.exe examples/demo_pubchem_py3dmol.py --id caffeine --style ball_and_stick

Styles: ball_and_stick (default), stick, ball
Outputs: HTML + XYZ under media/py3dmol_pubchem/
"""

from __future__ import annotations

import argparse
from pathlib import Path

from chemanim.connect import fetch_molecule_data
from chemanim.viewer_3d import show_py3dmol, write_xyz


def get_args():
    p = argparse.ArgumentParser(description="PubChem -> py3Dmol viewer")
    p.add_argument("--id", dest="identifier", default="caffeine", help="PubChem name or CID (default: caffeine)")
    p.add_argument("--style", dest="style", default="ball_and_stick", choices=["ball_and_stick", "stick", "ball"], help="Rendering style")
    p.add_argument("--outdir", dest="outdir", default="media/py3dmol_pubchem", help="Output directory")
    return p.parse_args()


def ensure_coords(data):
    coords = data.get("coords") or []
    atoms = data.get("atoms") or []
    if coords and len(coords) == len(atoms):
        return data
    # Attempt to add coords via RDKit if available and we have a SMILES
    smiles = getattr(data, "get", lambda k, d=None: d)("smiles") if isinstance(data, dict) else None
    if smiles:
        try:
            from chemanim.rdkit_adapter import molecule_data_from_smiles
            return molecule_data_from_smiles(smiles, add_h=True, dimensionality="3d")
        except Exception:
            pass
    raise ValueError("No coordinates available; PubChem fetch returned no 3D coords and RDKit fallback failed")


def main():
    args = get_args()
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = fetch_molecule_data(args.identifier)
    if not data:
        raise RuntimeError(f"Could not fetch PubChem data for {args.identifier}")

    data = ensure_coords(data)

    # Write XYZ
    xyz_path = write_xyz(out_dir / f"{args.identifier}.xyz", data)
    print(f"XYZ written to {xyz_path}")

    # Write HTML
    view = show_py3dmol(data, style=args.style, width=640, height=480)
    html_path = out_dir / f"{args.identifier}_{args.style}.html"
    view.write_html(str(html_path))
    print(f"py3Dmol {args.style} written to {html_path}")


if __name__ == "__main__":
    main()
