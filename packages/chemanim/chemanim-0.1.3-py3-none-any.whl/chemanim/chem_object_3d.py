"""3D chem objects for ball-and-stick style scenes."""

import numpy as np

try:
    from manimlib import *
    MANIM_AVAILABLE = True
except ImportError:
    try:
        from manim import *  # type: ignore
        MANIM_AVAILABLE = True
    except ImportError:  # pragma: no cover - optional dependency
        MANIM_AVAILABLE = False

        class Group:
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
            def set_opacity(self, *_):
                return self

        class VGroup(Group):
            pass

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

    class Cylinder(VGroup):
        def __init__(self, *_, **__):
            super().__init__()
        def move_to(self, *_ , **__):
            return self
        def put_start_and_end_on(self, *_ , **__):
            return self

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


class Atom3D(Group):
    def __init__(self, element, radius_scale=0.35, show_label=False, label_font_size=20, **kwargs):
        data = get_element_data(element) or {"symbol": str(element), "color": "#BBBBBB", "radius": 0.5}
        self.symbol = data.get("symbol", str(element))
        self.color = data.get("color", "#BBBBBB")
        # Initialize color before super init because ManimGL calls init_colors inside __init__
        
        super().__init__()
        
        self.base_radius = float(data.get("radius", 0.5)) * float(radius_scale)
        self.radius = self.base_radius

        self.resolution = kwargs.get("resolution", (16, 16))
        self.sphere = Sphere(
            radius=self.radius,
            color=self.color,
            resolution=self.resolution,
        )
        self.sphere.set_opacity(1.0)
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

    def set_color(self, color, opacity=None, recurse=True):
        """Set the color of the atom sphere."""
        self.color = color
        
        # Guard against early call from super().__init__ before sphere is created
        if hasattr(self, "sphere"):
            if opacity is not None:
                 self.sphere.set_opacity(opacity)
            self.sphere.set_color(color)
            try:
                 self.sphere.checkerboard_colors = [color, color]
            except Exception:
                 pass
        
        return self

    def set_sphere_scale(self, scale: float):
        scale = max(scale, 0.0)
        target_radius = self.base_radius * scale
        if target_radius <= 0:
            self.radius = 0.0
            self.sphere.set_opacity(0)
            # self.sphere.set_stroke(width=0) # Not supported in ManimGL
            return self

        if self.radius <= 0:
            factor = target_radius / self.base_radius
        else:
            factor = target_radius / self.radius

        self.sphere.set_opacity(1.0)
        # self.sphere.set_stroke(width=0)
        # self.sphere.set_fill(color=self.color, opacity=1.0)
        self.sphere.set_color(self.color)
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


class Bond3D(Group):
    def __init__(self, atom1, atom2, order=1, stroke_width=5, color=GREY, gap=0.12, method="line", **kwargs):
        super().__init__(**kwargs)
        self.atom1 = atom1
        self.atom2 = atom2
        self.order = order
        self.stroke_width = stroke_width
        self.color = color
        self.gap = gap
        self.method = method # "line" or "cylinder"
        self.ignore_atom_radius = False
        self._refresh_geometry()

    def _bond_endpoints(self):
        start = self.atom1.get_center()
        end = self.atom2.get_center()
        vec = end - start
        length = np.linalg.norm(vec)
        if length == 0:
            return None, None, None
        unit = vec / length
        
        if self.ignore_atom_radius:
            r1, r2 = 0.0, 0.0
        else:
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
            p1 = start + off
            p2 = end + off
            
            if self.method == "cylinder":
                # Create a Cylinder
                radius = self.stroke_width * 0.015 # Tune this multiplier
                # For safety, ensure non-zero height
                height = np.linalg.norm(p2 - p1)
                if height < 1e-6: continue
                
                cyl = Cylinder(radius=radius, height=height, color=self.color, resolution=(8, 8))
                
                # Cylinder by default is along Z? or Y? In ManimGL it is usually Z-axis centered at ORIGIN
                # We need to rotate and move it
                # Actually ManimGL surfaces are complex.
                # Easiest way in ManimGL for arbitrary start/end is to rotate it.
                # Center
                center = (p1 + p2) / 2
                cyl.move_to(center)
                
                # Direction
                v = p2 - p1
                # ManimGL Cylinder is ALONG Z-AXIS by default (height along Z)
                # Rotate from Z to v
                # We can use rotate to align.
                
                # Helper:
                curr_axis = np.array([0, 0, 1])
                target_axis = v / np.linalg.norm(v)
                
                # Rotation axis
                axis = np.cross(curr_axis, target_axis)
                if np.linalg.norm(axis) < 1e-6:
                    # Parallel
                    if np.dot(curr_axis, target_axis) < 0:
                        cyl.rotate(PI, axis=RIGHT)
                else:
                    angle = np.arccos(np.clip(np.dot(curr_axis, target_axis), -1.0, 1.0))
                    cyl.rotate(angle, axis=axis)
                    
                self.add(cyl)
                
            else:
                # Default Line
                line = Line(p1, p2, stroke_width=self.stroke_width, color=self.color)
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
        if MANIM_AVAILABLE and self.method != "cylinder":
            # Cylinder updaters are expensive/complex, skip for now
            self.add_updater(lambda m: m._refresh_geometry())
        return self


class ChemObject3D(Group):
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
        bond_method="cylinder",
        **kwargs,
    ):
        self.resolution = kwargs.pop("resolution", (16, 16))
        
        super().__init__(**kwargs)
        self.molecule_data = molecule_data or {}
        self.coord_scale = coord_scale
        self.center_coords = center_coords
        self.bond_stroke = bond_stroke
        self.bond_gap = bond_gap
        self.atom_radius_scale = atom_radius_scale
        self.show_labels = show_labels
        self.label_font_size = label_font_size
        self.show_labels = show_labels
        self.label_font_size = label_font_size
        self.render_style = render_style
        self.bond_method = kwargs.get("bond_method", "cylinder")
        # self.resolution already popped

        self.atoms = {}
        self.bonds = {}
        self.atoms_group = Group()
        self.bonds_group = Group()

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
                resolution=self.resolution
            )
            pos = coords[idx] if idx < len(coords) else np.zeros(3)
            atom.move_to(pos)
            self.atoms[idx] = atom
            self.atoms_group.add(atom)

        for b in bonds_data:
            i, j = b.get("aid1", 0) - 1, b.get("aid2", 0) - 1
            order = b.get("order", 1)
            if i in self.atoms and j in self.atoms:
                bond = Bond3D(
                    self.atoms[i], 
                    self.atoms[j], 
                    order=order, 
                    stroke_width=self.bond_stroke, 
                    gap=self.bond_gap,
                    method=self.bond_method
                )
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
            atom_scale = 3.0   # enlarge atoms to approx full VDW radius (0.35 * 3 ~= 1.05 scale relative to true coords)
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
