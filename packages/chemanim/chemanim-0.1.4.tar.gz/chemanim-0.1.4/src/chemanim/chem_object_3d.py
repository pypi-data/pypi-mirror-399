"""3D chem objects for ball-and-stick style scenes."""

import numpy as np

try:
    from manim import *  # type: ignore
    MANIM_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    MANIM_AVAILABLE = False

    class VGroup:
        def __init__(self, *_, **__):
            self.submobjects = []
        def add(self, *args):
            self.submobjects.extend(args)
            return self
        def move_to(self, *_):
            return self
        def shift(self, *_):
            return self
        def rotate(self, *_ , **__):
            return self
        def scale(self, *_ , **__):
            return self
        def clear(self):
            self.submobjects = []
            return self
        def get_center(self):
            return np.array([0.0, 0.0, 0.0])
        def add_updater(self, *_ , **__):
            return self

    class Line(VGroup):
        def __init__(self, *_ , **__):
            super().__init__()
        def put_start_and_end_on(self, *_ , **__):
            return self

    class Sphere(VGroup):
        def __init__(self, *_ , **__):
            super().__init__()
        def move_to(self, *_ , **__):
            return self

    class Text(VGroup):
        def __init__(self, *_ , **__):
            super().__init__()
        def move_to(self, *_ , **__):
            return self

    class Scene:
        def __init__(self, *_, **__):
            pass

    WHITE = "#FFFFFF"
    GREY = "#888888"
    BLACK = "#000000"
    OUT = np.array([0.0, 0.0, 1.0])

from .data import get_element_data


def _normalize_coords(raw_coords, center=True, scale=1.0):
    coords = np.array(raw_coords, dtype=float)
    if coords.ndim != 2 or coords.shape[1] < 2:
        raise ValueError("Coordinate array must be N x 2 or N x 3")
    if coords.shape[1] == 2:
        zeros = np.zeros((coords.shape[0], 1))
        coords = np.concatenate([coords, zeros], axis=1)
    if center:
        coords = coords - np.mean(coords, axis=0)
    if scale != 1.0:
        coords = coords * scale
    return coords


def _safe_normal(vector):
    trial = np.array([1.0, 0.0, 0.0])
    if np.linalg.norm(np.cross(vector, trial)) < 1e-6:
        trial = np.array([0.0, 1.0, 0.0])
    normal = np.cross(vector, trial)
    norm = np.linalg.norm(normal)
    if norm < 1e-6:
        return np.array([0.0, 0.0, 1.0])
    return normal / norm


def _is_bright(hex_color: str) -> bool:
    try:
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        r, g, b = tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        return (0.299 * r + 0.587 * g + 0.114 * b) > 0.7
    except Exception:
        return False


class Atom3D(VGroup):
    def __init__(self, element, radius_scale=0.35, show_label=False, label_font_size=20, **kwargs):
        super().__init__(**kwargs)
        data = get_element_data(element) or {"symbol": str(element), "color": "#BBBBBB", "radius": 0.5}
        self.symbol = data.get("symbol", str(element))
        self.color = data.get("color", "#BBBBBB")
        self.base_radius = float(data.get("radius", 0.5)) * float(radius_scale)
        self.radius = self.base_radius

        self.sphere = Sphere(
            radius=self.radius,
            color=self.color,
            fill_opacity=1.0,
            stroke_width=0,
            checkerboard_colors=[self.color, self.color],
        )
        self.add(self.sphere)

        if show_label:
            if MANIM_AVAILABLE:
                try:
                    color_hex = Color(self.color).to_hex()
                except Exception:
                    color_hex = str(self.color)
            else:
                color_hex = str(self.color)

            txt_color = BLACK if _is_bright(color_hex) else WHITE
            label = Text(self.symbol, font_size=label_font_size, color=txt_color)
            label.move_to(self.sphere.get_center())
            if MANIM_AVAILABLE:
                label.add_updater(lambda m: m.move_to(self.sphere.get_center()))
            self._label = label
            self.add(label)

    def set_sphere_scale(self, scale: float):
        scale = max(scale, 0.0)
        target_radius = self.base_radius * scale
        if target_radius <= 0:
            self.radius = 0.0
            self.sphere.set_opacity(0)
            self.sphere.set_stroke(width=0)
            return self

        if self.radius <= 0:
            factor = target_radius / self.base_radius
        else:
            factor = target_radius / self.radius

        self.sphere.set_opacity(1.0)
        self.sphere.set_stroke(width=0)
        self.sphere.set_fill(color=self.color, opacity=1.0)
        try:
            self.sphere.checkerboard_colors = [self.color, self.color]
        except Exception:
            pass
        self.sphere.scale(factor)
        self.radius = target_radius
        return self

    def move_to(self, *args, **kwargs):
        # Move the entire group so label stays attached to the sphere.
        super().move_to(*args, **kwargs)
        return self

    def get_center(self):
        if hasattr(self, "sphere"):
            return self.sphere.get_center()
        return super().get_center()


class Bond3D(VGroup):
    def __init__(self, atom1, atom2, order=1, stroke_width=5, color=GREY, gap=0.12, **kwargs):
        super().__init__(**kwargs)
        self.atom1 = atom1
        self.atom2 = atom2
        self.order = order
        self.stroke_width = stroke_width
        self.color = color
        self.gap = gap
        self._refresh_geometry()

    def _bond_endpoints(self):
        start = self.atom1.get_center()
        end = self.atom2.get_center()
        vec = end - start
        length = np.linalg.norm(vec)
        if length == 0:
            return None, None, None
        unit = vec / length
        r1 = getattr(self.atom1, "radius", 0.0)
        r2 = getattr(self.atom2, "radius", 0.0)
        start = start + unit * r1
        end = end - unit * r2
        return start, end, unit

    def _offsets(self, unit):
        if self.order == 1:
            return [np.zeros(3)]
        normal = _safe_normal(unit)
        if self.order == 2:
            return [normal * self.gap, -normal * self.gap]
        if self.order == 3:
            return [np.zeros(3), normal * self.gap * 1.2, -normal * self.gap * 1.2]
        return [np.zeros(3)]

    def _refresh_geometry(self):
        start, end, unit = self._bond_endpoints()
        try:
            self.submobjects = []
        except Exception:
            pass
        if start is None or end is None:
            return self

        offsets = self._offsets(unit)
        for off in offsets:
            line = Line(start + off, end + off, stroke_width=self.stroke_width, color=self.color)
            if MANIM_AVAILABLE:
                line.add_updater(lambda m, o=off: m.put_start_and_end_on(*(self._current_endpoints(o))))
            self.add(line)
        return self

    def _current_endpoints(self, offset):
        start, end, unit = self._bond_endpoints()
        if start is None or end is None:
            return np.array([0, 0, 0]), np.array([0, 0, 0])
        return start + offset, end + offset

    def enable_dynamic(self):
        if MANIM_AVAILABLE:
            self.add_updater(lambda m: m._refresh_geometry())
        return self


class ChemObject3D(VGroup):
    def __init__(
        self,
        molecule_data=None,
        coord_scale=0.7,
        center_coords=True,
        bond_stroke=5,
        bond_gap=0.12,
        atom_radius_scale=0.35,
        show_labels=False,
        label_font_size=18,
        render_style="ball_and_stick",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.molecule_data = molecule_data or {}
        self.coord_scale = coord_scale
        self.center_coords = center_coords
        self.bond_stroke = bond_stroke
        self.bond_gap = bond_gap
        self.atom_radius_scale = atom_radius_scale
        self.show_labels = show_labels
        self.label_font_size = label_font_size
        self.render_style = render_style

        self.atoms = {}
        self.bonds = {}
        self.atoms_group = VGroup()
        self.bonds_group = VGroup()

        if molecule_data:
            self._build()
            self.apply_render_style(self.render_style)

    def _collect_coords(self, atoms_data, coords_list):
        if atoms_data and all("coords" in a for a in atoms_data):
            raw = [a["coords"] for a in atoms_data]
        elif coords_list:
            raw = coords_list
        else:
            raise ValueError("ChemObject3D requires explicit coordinates in molecule_data")
        return _normalize_coords(raw, center=self.center_coords, scale=self.coord_scale)

    def _build(self):
        data = self.molecule_data
        atoms_data = data.get("atoms", [])
        bonds_data = data.get("bonds", [])
        coords_list = data.get("coords", [])

        coords = self._collect_coords(atoms_data, coords_list)

        for idx, atom_info in enumerate(atoms_data):
            element = atom_info.get("element") or atom_info.get("symbol") or "C"
            atom = Atom3D(
                element,
                radius_scale=self.atom_radius_scale,
                show_label=self.show_labels,
                label_font_size=self.label_font_size,
            )
            pos = coords[idx] if idx < len(coords) else np.zeros(3)
            atom.move_to(pos)
            self.atoms[idx] = atom
            self.atoms_group.add(atom)

        for b in bonds_data:
            i, j = b.get("aid1", 0) - 1, b.get("aid2", 0) - 1
            order = b.get("order", 1)
            if i in self.atoms and j in self.atoms:
                bond = Bond3D(self.atoms[i], self.atoms[j], order=order, stroke_width=self.bond_stroke, gap=self.bond_gap)
                self.bonds[(i, j)] = bond
                self.bonds_group.add(bond)

        self.add(self.bonds_group, self.atoms_group)

    def apply_render_style(self, style: str):
        """Adjust atom/bond visuals to mimic common 3D render styles.

        Styles: ball_and_stick (default), stick, wire, space_fill.
        """
        style_key = str(style).lower().replace("-", "_")

        if style_key == "stick":
            atom_scale = 0.12  # tiny caps
            bond_width = max(self.bond_stroke * 0.9, 3)
            bond_opacity = 1.0
        elif style_key in {"wire", "wireframe", "wire_frame"}:
            atom_scale = 0.0   # hide atoms
            bond_width = max(self.bond_stroke * 0.35, 1.5)
            bond_opacity = 1.0
        elif style_key in {"space_filling", "space_fill", "spacefill"}:
            atom_scale = 1.4   # enlarge atoms
            bond_width = 0.0   # hide bonds
            bond_opacity = 0.0
        else:  # ball_and_stick
            atom_scale = 1.0
            bond_width = self.bond_stroke
            bond_opacity = 1.0

        for atom in self.atoms.values():
            atom.set_sphere_scale(atom_scale)

        for bond in self.bonds.values():
            bond.stroke_width = bond_width
            bond.gap = self.bond_gap
            bond.set_opacity(bond_opacity)
            bond._refresh_geometry()

        return self

    def enable_dynamic_bonds(self):
        for bond in self.bonds.values():
            bond.enable_dynamic()
        return self

    def enable_label_billboarding(self, camera):
        """Keep atom labels facing the camera while following atom positions.

        Pass the active camera (e.g., ``self.camera`` inside a ThreeDScene).
        Safe no-op when labels are absent or camera lacks rotation helpers.
        """
        if not MANIM_AVAILABLE:
            return self

        frame = getattr(camera, "frame", camera)
        for atom in self.atoms.values():
            label = getattr(atom, "_label", None)
            if not label:
                continue

            # Cache label's original points to reapply rotation cleanly each frame.
            if not hasattr(label, "_billboard_ref_points"):
                label._billboard_ref_points = label.points.copy()

            def _bb_updater(m, a=atom, f=frame):
                m.points = m._billboard_ref_points.copy()
                m.move_to(a.get_center())
                try:
                    if hasattr(f, "get_inverse_camera_rotation_matrix"):
                        R = f.get_inverse_camera_rotation_matrix()
                        m.apply_matrix(R)
                except Exception:
                    pass
                return m

            label.add_updater(_bb_updater)

        return self

    def apply_coords(self, coords):
        coords = _normalize_coords(coords, center=self.center_coords, scale=self.coord_scale)
        for idx, coord in enumerate(coords):
            atom = self.atoms.get(idx)
            if atom:
                atom.move_to(coord)
        return self

    def rotate_molecule(self, angle, axis=OUT, about_point=None):
        self.rotate(angle, axis=axis, about_point=about_point)
        return self

    @classmethod
    def from_pubchem(cls, identifier, prefer_3d=True, **kwargs):
        from .connect import fetch_molecule_data

        data = fetch_molecule_data(identifier)
        if not data:
            raise ValueError(f"Could not fetch {identifier}")

        # Fallback: if only 2D coords and caller wants 3D, try RDKit embedding when SMILES present
        if prefer_3d and data.get("dimensionality", 2) < 3 and data.get("atoms") and not data.get("coords"):
            try:
                from .rdkit_adapter import molecule_data_from_smiles
                smiles = data.get("smiles")
                if smiles:
                    data = molecule_data_from_smiles(smiles, dimensionality="3d")
            except Exception:
                pass

        return cls(data, **kwargs)

    @classmethod
    def from_smiles_rdkit(cls, smiles, add_h=True, optimize_3d=True, random_seed=0, **kwargs):
        from .rdkit_adapter import molecule_data_from_smiles

        data = molecule_data_from_smiles(
            smiles,
            add_h=add_h,
            dimensionality="3d",
            optimize_3d=optimize_3d,
            random_seed=random_seed,
        )
        return cls(data, **kwargs)

    @classmethod
    def from_file(cls, filepath, **kwargs):
        import json
        from .connect import parse_pubchem_json

        with open(filepath, "r") as f:
            content = json.load(f)
        data = parse_pubchem_json(content)
        if not data:
            raise ValueError(f"Could not parse {filepath}")
        return cls(data, **kwargs)


CObject3D = ChemObject3D
