"""Lightweight helpers for external 3D viewers (py3Dmol, XYZ export)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List


def _require_py3dmol():
    try:
        import py3Dmol  # type: ignore  # noqa: F401
    except Exception as exc:
        raise ImportError(
            "py3Dmol is required for interactive 3D viewing. Install with `pip install py3Dmol`."
        ) from exc


def _coords_from_molecule(molecule_data: Dict[str, Any]) -> List[List[float]]:
    atoms = molecule_data.get("atoms") or []
    coords = []
    for atom in atoms:
        c = atom.get("coords")
        if c is None:
            raise ValueError("molecule_data atoms must include 'coords' for 3D viewing/export")
        if len(c) == 2:
            c = [c[0], c[1], 0.0]
        coords.append([float(c[0]), float(c[1]), float(c[2])])
    return coords


def molecule_to_xyz_string(molecule_data: Dict[str, Any]) -> str:
    atoms = molecule_data.get("atoms") or []
    coords = _coords_from_molecule(molecule_data)
    if len(atoms) != len(coords):
        raise ValueError("Atom count and coordinate count must match for XYZ export")

    lines = [str(len(atoms)), "chemanim export"]
    for atom, c in zip(atoms, coords):
        symbol = atom.get("element") or atom.get("symbol") or "C"
        lines.append(f"{symbol} {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}")
    return "\n".join(lines)


def write_xyz(path: str | Path, molecule_data: Dict[str, Any]) -> Path:
    path = Path(path)
    path.write_text(molecule_to_xyz_string(molecule_data), encoding="utf-8")
    return path


def show_py3dmol(
    molecule_data: Dict[str, Any],
    style: str = "ball_and_stick",
    background: str = "#ffffff",
    width: int = 640,
    height: int = 480,
    stick_radius: float = 0.18,
    sphere_scale: float = 0.28,
):
    """Render molecule_data in a py3Dmol view.

    Returns the py3Dmol view object so callers can further customize or write_html().
    """
    _require_py3dmol()
    import py3Dmol  # type: ignore

    xyz = molecule_to_xyz_string(molecule_data)

    view = py3Dmol.view(width=width, height=height)
    try:
        view.setBackgroundColor(background)
    except Exception:
        pass
    view.addModel(xyz, "xyz")

    s = style.lower().replace("-", "_")
    if s in {"ball", "spacefill", "space_filling", "spacefill"}:
        view.setStyle({"sphere": {"scale": max(sphere_scale, 0.1)}})
    elif s in {"stick", "sticks"}:
        view.setStyle({"stick": {"radius": max(stick_radius, 0.05)}})
    else:  # default ball-and-stick
        view.setStyle(
            {
                "stick": {"radius": max(stick_radius, 0.05)},
                "sphere": {"scale": max(sphere_scale, 0.1)},
            }
        )

    view.zoomTo()
    return view
