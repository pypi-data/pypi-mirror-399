"""Biochemistry module for macromolecules (proteins, DNA, etc.)

MIGRATED TO MANIMGL (from Manim Community Edition)
"""

try:
    from manimlib import *
    MANIMGL_AVAILABLE = True
except ImportError:
    MANIMGL_AVAILABLE = False
    # Minimal stubs so the module can import without ManimGL
    class Group:
        def __init__(self, *args, **kwargs):
            self.submobjects = list(args) if args else []
        def add(self, *args):
            self.submobjects.extend(args)
            return self
        def set_opacity(self, *_):
            return self

    class VGroup(Group):
        pass

    class VMobject(Group):
        def set_points_smoothly(self, *_):
            return self
        def set_stroke(self, **_):
            return self
        def point_from_proportion(self, u):
            return np.array([0, 0, 0])

    class Sphere(Group):
        def __init__(self, *args, **kwargs):
            pass
        def move_to(self, *args):
            return self

    class Surface(Group):
        def __init__(self, *args, **kwargs):
            pass
        def set_style(self, **_):
            return self

    BLUE = "#0000FF"
    BLUE_E = "#1C758A"
    RED = "#FF0000"
    YELLOW = "#FFFF00"
    GREEN = "#00FF00"
    GREY = "#888888"
    UP = np.array([0, 1, 0])
    RIGHT = np.array([1, 0, 0])
    PI = 3.14159265359

try:
    from Bio.PDB import PDBParser
except ImportError:
    PDBParser = None

try:
    import biotite.structure as struc
    import biotite.structure.io as strucio
    import biotite.structure.io.pdb as bio_pdb
    BIOTITE_AVAILABLE = True
except ImportError:
    BIOTITE_AVAILABLE = False


from .chem_object_3d import ChemObject3D, _normalize_coords
import numpy as np
import requests
import os

def _catmull_rom(p0, p1, p2, p3, t):
    """Calculate Catmull-Rom spline point at time t."""
    return 0.5 * (
        (2 * p1) +
        (-p0 + p2) * t +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 +
        (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
    )

def _catmull_rom_derivative(p0, p1, p2, p3, t):
    """Calculate derivative of Catmull-Rom spline at time t."""
    return 0.5 * (
        (-p0 + p2) +
        2 * (2 * p0 - 5 * p1 + 4 * p2 - p3) * t +
        3 * (-p0 + 3 * p1 - 3 * p2 + p3) * t**2
    )

try:
    from skimage import measure
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


class Protein(ChemObject3D):
    """A protein (or macromolecule) parsed from a PDB file."""

    def __init__(self, pdb_file, include_hydrogens=True, show_water=False, show_heteroatoms=False, **kwargs):
        if PDBParser is None:
            raise ImportError("Biopython is required for biochemistry features. Install it with pip install biopython.")

        self.pdb_file = pdb_file
        self.include_hydrogens = include_hydrogens
        self.show_water = show_water
        self.show_heteroatoms = show_heteroatoms

        molecule_data = self._parse_pdb_to_data()

        if "render_style" not in kwargs:
            kwargs["render_style"] = "sticks"

        super().__init__(molecule_data=molecule_data, **kwargs)

    @classmethod
    def from_uniprot(cls, uniprot_id: str, use_alphafold: bool = True, **kwargs):
        """Creates a Protein object by fetching data from UniProt/AlphaFold.
        
        Args:
            uniprot_id (str): The UniProt accession ID (e.g., P69905 for Hemoglobin A).
            use_alphafold (bool): If True, fetches the predicted structure from AlphaFold DB.
                                  If False, currently raises NotImplementedError (Experimental PDB selection is complex).
            **kwargs: Arguments passed to the Protein constructor.
        """
        # Simple cache in user's home or temp
        cache_dir = os.path.join(os.path.expanduser("~"), ".chemanim", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        if use_alphafold:
            # Try latest version first (v4)
            # URL format: https://alphafold.ebi.ac.uk/files/AF-{ACCESS}-F1-model_v4.pdb
            filename = f"AF-{uniprot_id}-F1-model_v4.pdb"
            filepath = os.path.join(cache_dir, filename)
            url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
            
            if not os.path.exists(filepath):
                print(f"Downloading AlphaFold structure for {uniprot_id}...")
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        print(f"Saved to {filepath}")
                    else:
                        raise IOError(f"Failed to download from AlphaFold ({url}): Status {response.status_code}")
                except Exception as e:
                    raise IOError(f"Network error downloading {uniprot_id}: {e}")
            else:
                print(f"Using cached file: {filepath}")
            
            return cls(filepath, **kwargs)
        else:
             raise NotImplementedError("Fetching experimental PDBs from UniProt metadata is not yet implemented. Please use AlphaFold mode or provide a PDB file directly.")

    def apply_render_style(self, style: str):
        def _set_group_opacity(name: str, opacity: float):
            group = getattr(self, name, None)
            if group:
                group.set_opacity(opacity)

        def _hide_optional_groups(except_groups=()):
            """Hide style-specific groups to avoid z-fighting when styles change."""
            keep = set(except_groups)
            for name in ("trace_group", "ribbon_group", "cartoon_group", "surface_group"):
                if name not in keep:
                    _set_group_opacity(name, 0)

        if style == "trace":
            _hide_optional_groups(("trace_group",))
            self.atoms_group.set_opacity(0)
            self.bonds_group.set_opacity(0)

            if not hasattr(self, "trace_group") or not self.trace_group:
                self.trace_group = self._create_backbone_trace()
                self.add(self.trace_group)
            self.trace_group.set_opacity(1)
            self.render_style = style

        elif style == "ribbon":
            _hide_optional_groups(("ribbon_group",))
            self.atoms_group.set_opacity(0)
            self.bonds_group.set_opacity(0)
            if hasattr(self, "trace_group") and self.trace_group:
                self.trace_group.set_opacity(0)

            if not hasattr(self, "ribbon_group") or not self.ribbon_group:
                self.ribbon_group = self._create_ribbon()
                self.add(self.ribbon_group)
            self.ribbon_group.set_opacity(1)
            self.render_style = style

        elif style == "cartoon":
            _hide_optional_groups(("cartoon_group",))
            self.atoms_group.set_opacity(0)
            self.bonds_group.set_opacity(0)
            if hasattr(self, "trace_group") and self.trace_group:
                self.trace_group.set_opacity(0)
            if hasattr(self, "ribbon_group") and self.ribbon_group:
                self.ribbon_group.set_opacity(0)

            if not hasattr(self, "cartoon_group") or not self.cartoon_group:
                self.cartoon_group = self._create_cartoon()
                self.add(self.cartoon_group)
            self.cartoon_group.set_opacity(1)
            self.render_style = style

        elif style == "ball_and_stick_sse":
            # Show atoms and bonds
            self.atoms_group.set_opacity(1)
            self.bonds_group.set_opacity(1)
            _hide_optional_groups(())
            
            # Apply SSE coloring
            self._apply_atom_colors()
            self.render_style = style

        elif style == "line_sse":
            # "Line" or "Stick" style usually implies showing just the bonds.
            # However, to make connections smooth ("seamless elbow"), we show atoms 
            # as small spheres with the same radius as the bonds.
            
            self.atoms_group.set_opacity(1)
            self.bonds_group.set_opacity(1)
            _hide_optional_groups(())
            
            # 1. Colors
            self._apply_atom_colors()
            
            # 2. Geometry Sizes: Joint Spheres
            # Bond3D uses: radius = self.bond_stroke * 0.015
            target_radius = self.bond_stroke * 0.015
            
            # Identify bonded atoms to hide isolated ones (floating dots)
            bonded_indices = set()
            for (i, j) in self.bonds.keys():
                bonded_indices.add(i)
                bonded_indices.add(j)

            for idx, atom in self.atoms.items():
                # Check data flags
                atom_data = self.molecule_data["atoms"][idx]
                is_water = atom_data.get("is_water", False)
                is_hetero = atom_data.get("is_hetero", False)
                
                # Logic for visibility
                should_show = False
                
                if idx in bonded_indices:
                    should_show = True
                
                # Override for solvent/hetero
                if is_water:
                    should_show = self.show_water
                elif is_hetero:
                    should_show = self.show_heteroatoms or (idx in bonded_indices) 
                    # Usually ions are single, so they won't be in bonded_indices unless we parse ionic bonds.
                    # If we want to show single ions, we must respect show_heteroatoms.

                if not should_show:
                    atom.set_sphere_scale(0)
                    continue
                
                # If showing a single ion/water, we probably want normal VDW radius or smaller?
                # In Stick mode, single atoms look weird if they are tiny stick-joints.
                # Let's say if NOT bonded, we show as Ball (scale=1.0 or user default).
                # If bonded, we show as Joint (target_radius).
                
                if idx in bonded_indices:
                    # Joint
                    if atom.base_radius > 0:
                        scale = target_radius / atom.base_radius
                        atom.set_sphere_scale(scale)
                    else:
                        atom.set_sphere_scale(0)
                else:
                    # Isolated (Water/Ion) -> Show as Ball (default radius)
                    # Use a moderate scale, e.g., 0.5 of VDW for cleaner look, or 1.0
                    atom.set_sphere_scale(0.5) 
                    # Ensure opacity is reset if it was hidden
                    atom.sphere.set_opacity(1)
                    
            # 3. Update Bond Colors & Refresh Geometry

                # Scale atom to match target radius exactly
                if atom.base_radius > 0:
                    scale = target_radius / atom.base_radius
                    atom.set_sphere_scale(scale)
                else:
                    atom.set_sphere_scale(0)
            
            # 3. Update Bond Colors & Refresh Geometry
            # Geometry refresh is needed to account for new atom radii (gap calculations)
            for bond in self.bonds.values():
                bond.ignore_atom_radius = True # Extend bond to center of atom for seamless joint
                bond.color = bond.atom1.color 
                bond._refresh_geometry()
                
            self.render_style = style
            
        elif style == "surface":
            # Update colors for surface generation
            self._apply_atom_colors()
            
            # Hide Atoms/Bonds/Cartoons
            self.atoms_group.set_opacity(0)
            self.bonds_group.set_opacity(0)
            _hide_optional_groups(("surface_group",))
            if hasattr(self, "trace_group") and self.trace_group:
                self.trace_group.set_opacity(0)
            if hasattr(self, "ribbon_group") and self.ribbon_group:
                self.ribbon_group.set_opacity(0)
            if hasattr(self, "cartoon_group") and self.cartoon_group:
                self.cartoon_group.set_opacity(0)
                
            if not hasattr(self, "surface_group") or not self.surface_group:
                self.surface_group = self._create_surface(style='gaussian')
                self.add(self.surface_group)
            self.surface_group.set_opacity(1)
            self.render_style = style
            
        else:
            _hide_optional_groups(())
            super().apply_render_style(style)

    def toggle_interactions(self, show=True):
        """Show or hide non-covalent interactions (Hydrogen Bonds).
        
        Tries to use Biotite's H-bond detection first (requires H atoms).
        Falls back to distance-based N-O/O-N heuristic (< 3.2A) if no H atoms found.
        """
        if show:
            if not hasattr(self, "interaction_group"):
                self.interaction_group = self._create_interactions()
                self.add(self.interaction_group)
            self.interaction_group.set_opacity(1)
        else:
            if hasattr(self, "interaction_group"):
                self.interaction_group.set_opacity(0)

    def _create_interactions(self):
        """Create dashed lines for interactions."""
        group = Group()
        
        if not BIOTITE_AVAILABLE:
            return group

        # Lazy load if missing
        if not hasattr(self, "biotite_atom_array") or self.biotite_atom_array is None:
            if hasattr(self, "pdb_file") and self.pdb_file:
                try:
                    loaded = strucio.load_structure(self.pdb_file)
                    if hasattr(loaded, "stack_depth") and loaded.stack_depth() > 0:
                         self.biotite_atom_array = loaded[0]
                    else:
                         self.biotite_atom_array = loaded
                except Exception as e:
                    print(f"Failed to lazy load structure: {e}")
                    return group
            else:
                return group
            
        triplets = []
        
        # 1. Try strict H-bond detection (Requires Hydrogens)
        try:
            # Check if H exists
            has_h = (self.biotite_atom_array.element == "H").any()
            if has_h:
                triplets = struc.hbond(self.biotite_atom_array)
        except Exception:
            pass
            
        coords = self.biotite_atom_array.coord
        norm_coords = _normalize_coords(coords, self.center_coords, self.coord_scale)
        
        # If strict detection worked
        if len(triplets) > 0:
            for d_i, h_i, a_i in triplets:
                p1 = norm_coords[h_i]
                p2 = norm_coords[a_i]
                line = DashedLine(p1, p2, color=YELLOW, stroke_width=2, dash_length=0.1)
                group.add(line)
        else:
            # 2. Naive Heuristic: N...O distance < 3.2A, > 2.0A
            # Optimization: Use CellList for speed
            try:
                # Filter indices for N and O
                mask_n = self.biotite_atom_array.element == "N"
                mask_o = self.biotite_atom_array.element == "O"
                indices_n = np.where(mask_n)[0]
                indices_o = np.where(mask_o)[0]
                
                if len(indices_n) > 0 and len(indices_o) > 0:
                    pos_n = coords[indices_n]
                    pos_o = coords[indices_o]
                    
                    # CellList for efficiency
                    cell_list = struc.CellList(pos_o, cell_size=3.5)
                    
                    for i, idx_n in enumerate(indices_n):
                        # Find O within 3.2A of this N
                        pos = pos_n[i]
                        indices_in_target = cell_list.get_atoms(pos, radius=3.2)
                        
                        for k in indices_in_target:
                            # Calculate distance manually
                            d = np.linalg.norm(pos_o[k] - pos)
                            
                            if d < 2.3: continue # Covalent bond exclusion
                            
                            idx_o = indices_o[k]
                            
                            p1 = norm_coords[idx_n]
                            p2 = norm_coords[idx_o]
                            
                            line = DashedLine(p1, p2, color=YELLOW, stroke_width=2, dash_length=0.1)
                            group.add(line)
            except Exception as e:
                print(f"Interaction detection failed: {e}")
                
        return group

    def _create_backbone_trace(self):
        """Create a smooth tubular backbone connecting Alpha Carbon atoms.
        
        Handles multiple chains and chain breaks by creating separate tubes.
        """
        # Dark teal color matching Mol* backbone style
        trace_color = "#2F5F5F"  
        radius = 0.10 * self.coord_scale
        
        # Collect Cα atoms with their chain info
        ca_atoms = [atom for atom in self.molecule_data["atoms"] if atom.get("name") == "CA"]
        
        if not ca_atoms:
            return Group()
            
        trace_group = Group()
        
        # Split into continuous segments (break at chain changes or large gaps)
        segments = []
        current_segment = []
        last_chain = None
        last_coords = None
        
        for atom in ca_atoms:
            chain_id = atom.get("chain_id", "A")
            coords = atom["coords"]
            
            # Check for chain break or large distance gap (> 4.5 Å between Cα atoms)
            should_break = False
            if last_chain is not None and chain_id != last_chain:
                should_break = True
            elif last_coords is not None:
                dist = np.linalg.norm(np.array(coords) - np.array(last_coords))
                if dist > 4.5:  # Typical Cα-Cα distance is ~3.8 Å
                    should_break = True
                    
            if should_break and current_segment:
                segments.append(current_segment)
                current_segment = []
                
            current_segment.append(coords)
            last_chain = chain_id
            last_coords = coords
            
        if current_segment:
            segments.append(current_segment)
            
        # Create tube for each continuous segment
        for segment_coords in segments:
            if len(segment_coords) >= 2:
                tube = self._create_smooth_tube(segment_coords, radius, trace_color)
                trace_group.add(tube)
                
        return trace_group

    def _create_smooth_tube(self, points, radius, color):
        """Create a trace using individual line segments.
        
        Uses separate Line objects to avoid VMobject fill artifacts in 3D.
        """
        if len(points) < 2:
            return Group()

        # Normalize points
        pts = _normalize_coords(points, center=self.center_coords, scale=self.coord_scale)
        
        trace = Group()

        # Convert radius to stroke width (thicker for visibility)
        stroke_width = radius * 450
        
        # Create individual line segments between consecutive points
        for i in range(len(pts) - 1):
            start = pts[i]
            end = pts[i + 1]
            
            # Create a simple 2-point line
            line = Line(start, end)
            line.set_stroke(color=color, width=stroke_width, opacity=1)
            trace.add(line)
        
        return trace

    def _create_ribbon(self):
        """Create a flat ribbon using Polygon quads with SSE-based width.
        
        Creates actual ribbon surfaces (flat quads) between Cα atoms.
        Helices and sheets are wider than coils.
        Uses Catmull-Rom splines for smoothness.
        """
        # SSE-based widths (half-width in scene units)
        sse_widths = {
            "H": 1.6,   # Helix - wide
            "E": 2.0,   # Sheet - widest
            "C": 0.6,   # Coil - thin
        }
        
        # Base grey color
        base_grey = 126

        ribbon = Group()
        
        # Get SSE annotation
        sse_map = self._get_sse_annotation() if BIOTITE_AVAILABLE else {}
        
        # Collect Cα atoms with normal hints from carbonyl O
        backbone = self._collect_backbone_points()
        if not backbone:
            return ribbon

        total_residues = sum(len(res) for _, res in backbone)
        global_res_idx = 0
            
        for chain_id, residues in backbone:
            res_count_in_chain = len(residues)
            current_base_idx = global_res_idx
            global_res_idx += res_count_in_chain
            if len(residues) < 2:
                continue
                
            # Build frames with proper normals
            frames = self._build_backbone_frames(residues)
            if len(frames) < 2:
                continue
            
            # Normalize points
            points = [f["point"] for f in frames]
            normals = [f["normal"] for f in frames]
            res_nums = [f.get("residue_number", i) for i, f in enumerate(frames)]
            res_names = [f.get("res_name", "UNK") for f in frames]
            
            pts = _normalize_coords(points, center=self.center_coords, scale=self.coord_scale)
            
            # Subdivide for smoother appearance - High value for smooth curves
            subdivisions = 8
            
            # Track previous edge to ensure consistent connection
            prev_v3 = None
            prev_v4 = None
            
            for i in range(len(pts) - 1):
                p1 = pts[i]
                p2 = pts[i + 1]
                
                # Neighbors for Spline
                p0 = pts[i - 1] if i > 0 else p1
                p3 = pts[i + 2] if i < len(pts) - 2 else p2
                
                n1 = normals[i]
                n2 = normals[i + 1]
                
                # Neighbors for Normal Spline
                n0 = normals[i - 1] if i > 0 else n1
                n3 = normals[i + 2] if i < len(normals) - 2 else n2
                
                # Get SSE type for this residue
                res_num = res_nums[i]
                sse_type = sse_map.get((chain_id, res_num), "C")
                width = sse_widths.get(sse_type, 0.6) * self.coord_scale

                # Color logic
                res_name_curr = res_names[i]
                base_color = self._get_residue_color(
                    chain_id, res_num, res_name_curr, 
                    current_base_idx + i, total_residues, 
                    sse_type=sse_type
                )
                
                for j in range(subdivisions):
                    t1 = j / subdivisions
                    t2 = (j + 1) / subdivisions
                    
                    # Interpolate positions and normals using Catmull-Rom
                    pt1 = _catmull_rom(p0, p1, p2, p3, t1)
                    pt2 = _catmull_rom(p0, p1, p2, p3, t2)
                    
                    nt1 = _catmull_rom(n0, n1, n2, n3, t1)
                    nt2 = _catmull_rom(n0, n1, n2, n3, t2)
                    
                    # Normalize interpolated normals
                    if np.linalg.norm(nt1) > 0:
                        nt1 = nt1 / np.linalg.norm(nt1)
                    if np.linalg.norm(nt2) > 0:
                        nt2 = nt2 / np.linalg.norm(nt2)
                    
                    # Create quad corners
                    if prev_v3 is not None and j == 0:
                        v1 = prev_v4
                        v2 = prev_v3
                    else:
                        v1 = pt1 + nt1 * width
                        v2 = pt1 - nt1 * width
                    
                    v3 = pt2 - nt2 * width
                    v4 = pt2 + nt2 * width
                    
                    # Simple shading based on face orientation
                    edge1 = v2 - v1
                    edge2 = v4 - v1
                    face_normal = np.cross(edge1, edge2)
                    norm_len = np.linalg.norm(face_normal)
                    if norm_len > 0:
                        face_normal = face_normal / norm_len
                    
                    light_dir = np.array([0.3, 0.3, 1.0])
                    light_dir = light_dir / np.linalg.norm(light_dir)
                    diffuse = np.abs(np.dot(face_normal, light_dir))
                    intensity = 0.5 + 0.5 * diffuse
                    
                    if MANIMGL_AVAILABLE:
                         # Shading with proper color
                         try:
                             base_rgb = color_to_rgb(base_color)
                             shaded_rgb = np.clip(base_rgb * intensity, 0, 1)
                             shaded_hex = rgb_to_hex(shaded_rgb)
                         except Exception:
                             grey_val = int(126 * intensity)
                             shaded_hex = f'#{grey_val:02x}{grey_val:02x}{grey_val:02x}'
                    else:
                         grey_val = int(base_grey * intensity)
                         shaded_hex = f'#{grey_val:02x}{grey_val:02x}{grey_val:02x}'
                    
                    # Create polygon with consistent vertex order
                    poly = Polygon(v1, v2, v3, v4, color=shaded_hex, fill_opacity=1, stroke_width=0, stroke_opacity=0)
                    ribbon.add(poly)
                    
                    # Store for next iteration
                    if j == subdivisions - 1:
                        prev_v3 = v3
                        prev_v4 = v4
        
        return ribbon
    
    def _get_sse_annotation(self):
        """Get SSE (Secondary Structure Element) annotation using biotite."""
        if not BIOTITE_AVAILABLE:
            print("SSE: Biotite not available")
            return {}
            
        try:
            atom_array = strucio.load_structure(self.pdb_file)
            if hasattr(atom_array, 'get_array'):
                atom_array = atom_array.get_array(0)
            
            # Compute SSE - returns one code per residue
            sse = struc.annotate_sse(atom_array)
            
            # Get residue start indices
            res_starts = struc.get_residue_starts(atom_array)
            
            # Build map using residue start indices to get chain_id and res_id
            sse_map = {}
            helix_count = 0
            sheet_count = 0
            coil_count = 0
            
            for i, start_idx in enumerate(res_starts):
                if i >= len(sse):
                    break
                chain_id = atom_array.chain_id[start_idx]
                res_id = atom_array.res_id[start_idx]
                sse_code = sse[i]
                
                key = (chain_id, res_id)
                if sse_code == 'a':
                    sse_map[key] = "H"
                    helix_count += 1
                elif sse_code == 'b':
                    sse_map[key] = "E"
                    sheet_count += 1
                else:
                    sse_map[key] = "C"
                    coil_count += 1
            
            print(f"SSE map: Helix={helix_count}, Sheet={sheet_count}, Coil={coil_count}")
            
            return sse_map
        except Exception as e:
            print(f"SSE annotation failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _collect_backbone_points(self):
        """Collect CA points with an orientation hint from the carbonyl oxygen."""
        atoms = self.molecule_data["atoms"]
        residues = {}
        order = []

        for atom in atoms:
            name = atom.get("name", "")
            if name not in ("CA", "O", "O'"):
                continue

            chain = atom.get("chain", "")
            res_no = atom.get("residue_number")
            ins_code = atom.get("insertion_code", "")
            key = (chain, res_no, ins_code)

            if key not in residues:
                residues[key] = {
                    "ca": None, 
                    "o": None, 
                    "chain": chain, 
                    "res_no": res_no,
                    "res_name": atom.get("residue_name", "UNK")
                }
                order.append(key)

            if name == "CA":
                residues[key]["ca"] = np.array(atom["coords"])
            else:
                residues[key]["o"] = np.array(atom["coords"])

        # Preserve the original PDB ordering per chain
        chain_map = {}
        chain_keys = []
        for key in order:
            entry = residues[key]
            if entry["ca"] is None:
                continue
            normal_hint = None
            if entry["o"] is not None:
                normal_hint = entry["o"] - entry["ca"]

            chain = entry["chain"]
            if chain not in chain_map:
                chain_map[chain] = []
                chain_keys.append(chain)

            chain_map[chain].append({
                "point": entry["ca"],
                "normal_hint": normal_hint,
                "residue_number": entry["res_no"],
                "res_name": entry.get("res_name", "UNK")
            })

        return [(chain, chain_map[chain]) for chain in chain_keys]

    def _build_backbone_frames(self, entries):
        """Compute smoothed Frenet-like frames for the ribbon strip."""
        if not entries:
            return []

        points = [e["point"] for e in entries]
        hints = [e.get("normal_hint") for e in entries]
        res_nums = [e.get("residue_number") for e in entries]
        res_names = [e.get("res_name", "UNK") for e in entries]

        if len(points) == 1:
            default_normal = np.array([0.0, 0.0, 1.0])
            return [{"point": points[0], "normal": default_normal, "residue_number": res_nums[0], "res_name": res_names[0]}]

        tangents = []
        for i in range(len(points)):
            if i == 0:
                t = points[1] - points[0]
            elif i == len(points) - 1:
                t = points[-1] - points[-2]
            else:
                t = points[i + 1] - points[i - 1]

            if np.linalg.norm(t) < 1e-6:
                t = np.array([1.0, 0.0, 0.0])
            tangents.append(t / np.linalg.norm(t))

        frames = []
        prev_binormal = None

        for i, (point, tangent, hint) in enumerate(zip(points, tangents, hints)):
            res_num = res_nums[i] if i < len(res_nums) else None
            res_name = res_names[i] if i < len(res_names) else "UNK"
            normal = None
            if hint is not None and np.linalg.norm(hint) > 1e-6:
                projected = hint - np.dot(hint, tangent) * tangent
                if np.linalg.norm(projected) > 1e-6:
                    normal = projected / np.linalg.norm(projected)

            if normal is None:
                candidate = prev_binormal if prev_binormal is not None else np.array([0.0, 0.0, 1.0])
                if np.linalg.norm(np.cross(tangent, candidate)) < 1e-3:
                    candidate = np.array([0.0, 1.0, 0.0])
                normal = candidate - np.dot(candidate, tangent) * tangent
                if np.linalg.norm(normal) < 1e-6:
                    normal = np.array([1.0, 0.0, 0.0])
                normal = normal / np.linalg.norm(normal)

            binormal = np.cross(tangent, normal)
            if np.linalg.norm(binormal) < 1e-6:
                binormal = prev_binormal if prev_binormal is not None else np.array([1.0, 0.0, 0.0])
            binormal = binormal / np.linalg.norm(binormal)

            # Re-orthogonalize normal for numerical stability
            normal = np.cross(binormal, tangent)
            normal = normal / np.linalg.norm(normal)

            prev_binormal = binormal
            frames.append({"point": point, "normal": normal, "residue_number": res_num, "res_name": res_name})

        if len(frames) > 2:
            smoothed = []
            for idx, frame in enumerate(frames):
                start = max(0, idx - 1)
                end = min(len(frames), idx + 2)
                avg = np.sum([frames[j]["normal"] for j in range(start, end)], axis=0)
                avg = avg / np.linalg.norm(avg)
                smoothed.append({"point": frame["point"], "normal": avg, "residue_number": frame.get("residue_number"), "res_name": frame.get("res_name")})
            frames = smoothed

        return frames

    def _make_strip(self, points, normals, target_group, color=BLUE, width_scale=0.35):
        if len(points) < 4:
            return

        pts = _normalize_coords(points, center=self.center_coords, scale=self.coord_scale)
        ors = []
        for n in normals:
            if np.linalg.norm(n) < 1e-6:
                ors.append(np.array([0.0, 0.0, 1.0]))
            else:
                ors.append(n / np.linalg.norm(n))

        path = VMobject()
        path.set_points_smoothly(pts)

        def func(u, v):
            p = path.point_from_proportion(u)

            idx = u * (len(ors) - 1)
            i = int(idx)
            rem = idx - i
            if i >= len(ors) - 1:
                n_vec = ors[-1]
            else:
                n_vec = (1 - rem) * ors[i] + rem * ors[i + 1]

            t_u = min(u + 0.01, 1)
            p_next = path.point_from_proportion(t_u)
            tangent = p_next - p
            if np.linalg.norm(tangent) == 0:
                tangent = np.array([0.0, 0.0, 1.0])

            binormal = np.cross(tangent, n_vec)
            if np.linalg.norm(binormal) < 1e-3:
                binormal = np.array([1.0, 0.0, 0.0])
            binormal = binormal / np.linalg.norm(binormal)

            width = width_scale * self.coord_scale

            return p + binormal * (v * width)

        try:
            res_u = max(len(points) * 2, 12)

            if MANIMGL_AVAILABLE:
                surf = ParametricSurface(
                    func,
                    u_range=(0, 1),
                    v_range=(-1, 1),
                    resolution=(res_u, 2),
                    color=color
                )
            else:
                surf = Surface(
                    func,
                    u_range=[0, 1],
                    v_range=[-1, 1],
                    resolution=(res_u, 2),
                    color=color
                )

            surf.set_opacity(1.0)
            if hasattr(surf, "set_stroke"):
                surf.set_stroke(color=BLUE_E, width=0)
            target_group.add(surf)
        except Exception as e:
            print(f"DEBUG: Error creating surface: {e}")

    def _compute_sse(self):
        """Compute secondary structure elements using Biotite."""
        if not BIOTITE_AVAILABLE:
            print("Warning: Biotite not installed, cannot compute SSE.")
            return [], [], None

        pdb_file = bio_pdb.PDBFile.read(self.pdb_file)
        array = pdb_file.get_structure(model=1)
        sse = struc.annotate_sse(array)
        residues, _ = struc.get_residues(array)
        return sse, residues, array

    # Color Schemes
    _AMINO_COLORS = {
        'ALA': '#C8C8C8', 'ARG': '#145AFF', 'ASN': '#00DCDC', 'ASP': '#E60A0A',
        'CYS': '#E6E600', 'GLN': '#00DCDC', 'GLU': '#E60A0A', 'GLY': '#EBEBEB',
        'HIS': '#8282D2', 'ILE': '#0F820F', 'LEU': '#0F820F', 'LYS': '#145AFF',
        'MET': '#E6E600', 'PHE': '#3232AA', 'PRO': '#DC9682', 'SER': '#FA9600',
        'THR': '#FA9600', 'TRP': '#B45AB4', 'TYR': '#3232AA', 'VAL': '#0F820F',
    }
    _HYDROPHOBICITY = {
        'ILE': 4.5, 'VAL': 4.2, 'LEU': 3.8, 'PHE': 2.8, 'CYS': 2.5,
        'MET': 1.9, 'ALA': 1.8, 'GLY': -0.4, 'THR': -0.7, 'SER': -0.8,
        'TRP': -0.9, 'TYR': -1.3, 'PRO': -1.6, 'HIS': -3.2, 'GLU': -3.5,
        'GLN': -3.5, 'ASP': -3.5, 'ASN': -3.5, 'LYS': -3.9, 'ARG': -4.5
    }
    _CHAIN_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

    def set_color_scheme(self, scheme="sse", **kwargs):
        """Set the color scheme and refresh.
        
        Schemes: 'sse', 'chain', 'amino_acid', 'rainbow', 'hydrophobicity', 'asa'.
        """
        self.color_scheme = scheme
        self.color_scheme_kwargs = kwargs
        
        # Pre-calculate ASA if needed
        if scheme == "asa" and BIOTITE_AVAILABLE:
            if not hasattr(self, "_sasa_cache"):
                try:
                    self._sasa_cache = struc.sasa(self.biotite_atom_array, point_number=100)
                    # This is per atom. We need per residue.
                    # Aggregate SASA per residue.
                    res_starts = struc.get_residue_starts(self.biotite_atom_array)
                    res_sasa = {}
                    for i in range(len(res_starts)):
                        start = res_starts[i]
                        end = res_starts[i+1] if i < len(res_starts)-1 else len(self.biotite_atom_array)
                        # Identify residue
                        atom = self.biotite_atom_array[start]
                        key = (atom.chain_id, atom.res_id) # Using Biotite fields
                        
                        # Sum max sasa or mean? Usually SUM for residue area.
                        sasa_val = np.sum(self._sasa_cache[start:end])
                        res_sasa[key] = sasa_val
                    self._res_sasa = res_sasa
                except Exception as e:
                    print(f"ASA calculation failed: {e}")
                    self.color_scheme = "sse"

        # Re-apply current style to update colors
        if hasattr(self, "render_style"):
            # Clear existing geometry groups to force regeneration
            if hasattr(self, "cartoon_group"): 
                self.cartoon_group = None
            if hasattr(self, "ribbon_group"):
                self.ribbon_group = None
            if hasattr(self, "surface_group"):
                self.surface_group = None
            if hasattr(self, "ribbon_group"):
                self.ribbon_group = None
                
            self.apply_render_style(self.render_style)

    def _get_residue_color(self, chain_id, res_num, res_name, current_idx, total_residues, sse_type="C"):
        """Resolve color based on current scheme."""
        scheme = getattr(self, "color_scheme", "sse")
        
        if scheme == "sse":
            sse_colors = {"H": "#C2185B", "E": "#FDD835", "C": "#9E9E9E"}
            return sse_colors.get(sse_type, "#9E9E9E")
            
        elif scheme == "chain":
            # Hash chain_id to index
            idx = abs(hash(chain_id)) % len(self._CHAIN_COLORS)
            return self._CHAIN_COLORS[idx]
            
        elif scheme == "amino_acid":
            return self._AMINO_COLORS.get(res_name, "#888888")
            
        elif scheme == "rainbow":
            if total_residues < 1: return "#888888"
            # Blue (240) to Red (0)
            hue = 240 * (1 - current_idx / total_residues)
            return Color(hsl=(hue/360, 1.0, 0.5)).get_hex()
            
        elif scheme == "hydrophobicity":
            val = self._HYDROPHOBICITY.get(res_name, 0.0)
            # Scale: -4.5 (Hydrophilic/Red/Blue?) to 4.5 (Hydrophobic)
            # Common: Hydrophobic=Red, Hydrophilic=Blue? Or White-Red?
            # Let's map -4.5 -> Blue, 0 -> White, 4.5 -> Red
            norm = (val + 4.5) / 9.0 # 0 to 1
            norm = np.clip(norm, 0, 1)
            # Blue (.66) to Red (0.0)
            # Using interpolate_color logic or Manim Color
            # Simpler: Blue=0.66, White via Saturation?
            # Let's use Red-White-Blue manually
            if norm < 0.5:
                # 0.0 (Blue) -> 0.5 (White)
                t = norm * 2
                return interpolate_color(Color(BLUE), Color(WHITE), t).get_hex()
            else:
                # 0.5 (White) -> 1.0 (Red)
                t = (norm - 0.5) * 2
                return interpolate_color(Color(WHITE), Color(RED), t).get_hex()
                
        elif scheme == "asa":
            if hasattr(self, "_res_sasa"):
                sasa = self._res_sasa.get((chain_id, res_num), 0)
                # Map SASA (0 to ~200) to Gradient
                # Low ASA (Buried) = Grey/Blue? High ASA (Exposed) = Red/Orange?
                t = np.clip(sasa / 150.0, 0, 1)
                return interpolate_color(Color(GREY), Color(RED), t).get_hex()
            
        return "#9E9E9E"

    def _apply_atom_colors(self):
        """Update atom colors based on scheme."""
        sse_list, residues, _ = self._compute_sse()
        total_residues = len(residues)
        
        # Iterate atoms
        current_res_key = None
        global_res_idx = -1
        
        for i, atom_data in enumerate(self.molecule_data["atoms"]):
            key = (atom_data.get("chain"), atom_data.get("residue_number"), atom_data.get("insertion_code"))
            
            if key != current_res_key:
                current_res_key = key
                global_res_idx += 1
                
            # Get info
            chain = atom_data.get("chain", "")
            res_num = atom_data.get("residue_number")
            res_name = atom_data.get("residue_name", "UNK")
            
            # Map SSE code
            sse_type = "C"
            if global_res_idx < len(sse_list):
                 code = sse_list[global_res_idx]
                 sse_type = "H" if code == 'a' else ("E" if code == 'b' else "C")
                 
            color = self._get_residue_color(chain, res_num, res_name, global_res_idx, total_residues, sse_type)
            
            # Apply
            if i in self.atoms:
                 atom = self.atoms[i]
                 atom.sphere.set_color(color)
                 atom.color = color 

        
    def _create_cartoon(self):
        """Create a cartoon representation.
        
        Adapted from ribbon mode:
        - **3D Extruded Profile**: Handles smooth transition between Flat (Helix/Sheet) and Tube (Coil).
        - **Variable Profile**: Defined by width and thickness.
        - **Arrowheads**: Flared and tapered for Sheets/Helices.
        - **Splines**: Uses Catmull-Rom interpolation for smoothness.
        """
        # SSE Coloring
        sse_colors = {
            "H": "#C2185B",  # Magenta/Pink for Helix
            "E": "#FDD835",  # Yellow for Sheet
            "C": "#9E9E9E",  # Grey for Coil
        }

        # SSE-based Dimensions (half-width, half-thickness)
        # Helix/Sheet: Wide and thin (Flat)
        # Coil: Moderate and thick (Square/Round Tube)
        sse_dims = {
            "H": (1.6, 0.2),
            "E": (2.0, 0.2),
            "C": (0.3, 0.3), # Square tube radius 0.3 (Diameter 0.6)
        }
        
        cartoon = Group()

        def _color_to_rgb(color_value):
            """Normalize any color input to an RGB array."""
            try:
                return np.array(Color(color_value).get_rgb())
            except Exception:
                try:
                    hex_str = str(color_value).lstrip("#")
                    if len(hex_str) == 3:
                        hex_str = "".join(c * 2 for c in hex_str)
                    if len(hex_str) == 6:
                        return np.array([int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
                except Exception:
                    pass
            return np.array([0.5, 0.5, 0.5])
        
        # Get SSE annotation
        sse_map = self._get_sse_annotation() if BIOTITE_AVAILABLE else {}
        
        # Collect Cα atoms with normal hints from carbonyl O
        backbone = self._collect_backbone_points()
        if not backbone:
            return cartoon

        total_residues = sum(len(res) for _, res in backbone)
        global_res_idx = 0
            
        for chain_id, residues in backbone:
            res_count_in_chain = len(residues)
            current_base_idx = global_res_idx
            global_res_idx += res_count_in_chain
            if len(residues) < 2:
                continue
                
            # Build frames with proper normals
            frames = self._build_backbone_frames(residues)
            if len(frames) < 2:
                continue
            
            # Normalize points
            points = [f["point"] for f in frames]
            normals = [f["normal"] for f in frames]
            res_nums = [f.get("residue_number", i) for i, f in enumerate(frames)]
            res_names = [f.get("res_name", "UNK") for f in frames]
            
            # CRITICAL FIX: Align normals to prevent twisting
            # Beta sheets have alternating C=O directions (Up/Down).
            # We must flip them to be consistent so the ribbon doesn't twist 180 deg every residue.
            for n_idx in range(1, len(normals)):
                if np.dot(normals[n_idx], normals[n_idx-1]) < 0:
                    normals[n_idx] = -normals[n_idx]
            
            pts = _normalize_coords(points, center=self.center_coords, scale=self.coord_scale)
            
            # Subdivide for smoother appearance (Increased for Splines)
            subdivisions = 8
            
            # Track previous corners (4 corners for box profile)
            prev_corners = None
            
            for i in range(len(pts) - 1):
                p1 = pts[i]
                p2 = pts[i + 1]
                
                # Neighbors for Spline
                p0 = pts[i - 1] if i > 0 else p1
                p3 = pts[i + 2] if i < len(pts) - 2 else p2
                
                n1 = normals[i]
                n2 = normals[i + 1]
                
                # Neighbors for Normal Spline
                n0 = normals[i - 1] if i > 0 else n1
                n3 = normals[i + 2] if i < len(normals) - 2 else n2
                
                # Get SSE type for current and next residue
                res_num_curr = res_nums[i]
                res_num_next = res_nums[i+1]
                
                type_curr = sse_map.get((chain_id, res_num_curr), "C")
                type_next = sse_map.get((chain_id, res_num_next), "C")
                
                # Base dimensions
                # H/E thickness 0.05 for "completely flat" look. Coil thickness 0.25 (reduced).
                dims_map = {
                    "H": (1.6, 0.05),
                    "E": (2.0, 0.05),
                    "C": (0.25, 0.25),
                }
                
                dims = dims_map.get(type_curr, (0.25, 0.25))
                
                # Start and End dimensions match CURRENT type (no interpolation to next type)
                wc, hc = dims[0] * self.coord_scale, dims[1] * self.coord_scale
                wn, hn = wc, hc

                # Detect Arrowhead (End of Sheet or Helix)
                force_break = False
                
                # Sheets and Helices get Arrows at end
                if type_curr in ["E", "H"] and type_next != type_curr:
                    # Flared Arrow: Start wider than normal, taper to point
                    wc = wc * 1.6
                    wn = 0.0
                    hn = 0.0 # Taper thickness too
                    force_break = True # Disconnect from previous segment to make the barb sharp

                # Color choice based on scheme
                res_name_curr = res_names[i]
                color_hex = self._get_residue_color(
                    chain_id, res_num_curr, res_name_curr, 
                    current_base_idx + i, total_residues, 
                    sse_type=type_curr
                )

                for j in range(subdivisions):
                    t1 = j / subdivisions
                    t2 = (j + 1) / subdivisions
                    
                    # Interpolate using Catmull-Rom
                    pt1 = _catmull_rom(p0, p1, p2, p3, t1)
                    pt2 = _catmull_rom(p0, p1, p2, p3, t2)
                    
                    nt1 = _catmull_rom(n0, n1, n2, n3, t1)
                    nt2 = _catmull_rom(n0, n1, n2, n3, t2)
                    
                    tangent1 = _catmull_rom_derivative(p0, p1, p2, p3, t1)
                    tangent2 = _catmull_rom_derivative(p0, p1, p2, p3, t2)
                    
                    # Orthonormalize Frames
                    def get_frame(tan, norm):
                        tan_norm = np.linalg.norm(tan)
                        if tan_norm > 0: tan = tan / tan_norm
                        
                        # Orthogonalize normal to tangent
                        norm = norm - np.dot(norm, tan) * tan
                        norm_len = np.linalg.norm(norm)
                        if norm_len > 0: norm = norm / norm_len
                        else: norm = np.array([0, 0, 1]) # Fallback
                        
                        binorm = np.cross(tan, norm)
                        return tan, norm, binorm
                    
                    _, N1, B1 = get_frame(tangent1, nt1)
                    _, N2, B2 = get_frame(tangent2, nt2)
                    
                    # Interpolate dimensions linearly
                    w1 = wc * (1 - t1) + wn * t1
                    h1 = hc * (1 - t1) + hn * t1
                    w2 = wc * (1 - t2) + wn * t2
                    h2 = hc * (1 - t2) + hn * t2
                    
                    # Determine profile resolution
                    # Coils = Round (12 sides), H/E = Single Flat Strip (1 Face)
                    # sides=1 triggers special "Strip" logic avoiding Z-fighting of 2-sided mesh.
                    sides = 12 if type_curr == "C" else 1
                    
                    # Generate profile vertices
                    def get_profile_verts(pt, N, B, w, h, num_sides):
                        verts = []
                        if num_sides == 1:
                            # Single Flat Strip (Edge-to-Edge)
                            # Returns [Left, Right]
                            return [
                                pt + N * w,
                                pt - N * w
                            ]
                        else:
                            # Ellipse/Circle Profile (Tube)
                            for k in range(num_sides):
                                angle = 2 * np.pi * k / num_sides
                                # Use cos/sin for ellipse
                                v = pt + N * (w * np.cos(angle)) + B * (h * np.sin(angle))
                                verts.append(v)
                        return verts

                    c1_list = get_profile_verts(pt1, N1, B1, w1, h1, sides) # Current Start
                    c2_list = get_profile_verts(pt2, N2, B2, w2, h2, sides) # Current End
                    
                    # Check continuity
                    res_num_prev = res_nums[i-1] if i > 0 else -1
                    type_prev = sse_map.get((chain_id, res_num_prev), "C") if i > 0 else "C"
                    
                    use_prev = (prev_corners is not None and j == 0)
                    
                    # Don't use prev if:
                    # 1. Type changed (Step change in dims or profile shape)
                    # 2. We are forcing a break (Arrow barb)
                    if j == 0 and (type_curr != type_prev or force_break):
                         use_prev = False
                    
                    # If prev profile has different # of vertices, we can't connect seamlessly anyway
                    if use_prev and len(prev_corners) != len(c1_list):
                        use_prev = False
                    
                    if use_prev:
                        start_corners = prev_corners
                    else:
                        start_corners = c1_list
                    
                    end_corners = c2_list
                    
                    if sides == 1:
                        # Special Case: Single Ribbon Strip (One Quad)
                        # c1_list = [v1_start, v2_start]
                        v1 = start_corners[0]
                        v2 = start_corners[1]
                        v3 = end_corners[1]
                        v4 = end_corners[0]
                        
                        # Calculate Normal
                        edge1 = v2 - v1
                        edge2 = v4 - v1
                        face_normal = np.cross(edge1, edge2)
                        norm_len = np.linalg.norm(face_normal)
                        if norm_len > 0: face_normal /= norm_len
                        
                        light_dir = np.array([0.3, 0.3, 1.0])
                        light_dir /= np.linalg.norm(light_dir)
                        diffuse = np.abs(np.dot(face_normal, light_dir))
                        intensity = 0.5 + 0.5 * diffuse
                        
                        base_rgb = _color_to_rgb(color_hex)
                        shaded_rgb = np.clip(base_rgb * intensity, 0, 1)
                        shaded_hex = '#' + ''.join([f'{int(c*255):02x}' for c in shaded_rgb])
                        
                        poly = Polygon(v1, v2, v3, v4, color=shaded_hex, fill_opacity=1, stroke_width=0, stroke_opacity=0)
                        cartoon.add(poly)

                    else:
                        # Tube / Multi-face Profile
                        for k in range(sides):
                            # Quad: start[k], start[k+1], end[k+1], end[k]
                            k_next = (k + 1) % sides
                            
                            v1 = start_corners[k]
                            v2 = start_corners[k_next]
                            v3 = end_corners[k_next]
                            v4 = end_corners[k]
                            
                            # Shading
                            edge1 = v2 - v1
                            edge2 = v4 - v1
                            face_normal = np.cross(edge1, edge2)
                            norm_len = np.linalg.norm(face_normal)
                            if norm_len > 0: face_normal /= norm_len
                            
                            light_dir = np.array([0.3, 0.3, 1.0])
                            light_dir /= np.linalg.norm(light_dir)
                            diffuse = np.abs(np.dot(face_normal, light_dir))
                            intensity = 0.5 + 0.5 * diffuse
                            
                            base_rgb = _color_to_rgb(color_hex)
                            shaded_rgb = np.clip(base_rgb * intensity, 0, 1)
                            shaded_hex = '#' + ''.join([f'{int(c*255):02x}' for c in shaded_rgb])
                            
                            poly = Polygon(v1, v2, v3, v4, color=shaded_hex, fill_opacity=1, stroke_width=0, stroke_opacity=0)
                            cartoon.add(poly)
                    
                    if j == subdivisions - 1:
                        prev_corners = end_corners
        
        return cartoon

    def _render_smooth_segment(self, group, points, normal_hints, sse_type):
        """Render a segment of secondary structure using smooth surfaces."""
        if len(points) < 2: return

        # Styles
        if sse_type == 'a':  # Alpha Helix
            color = "#E91E63"  # Pink
            radius = 0.24 * self.coord_scale
            # Helices are tubes
            group.add(self._create_smooth_tube(points, radius, color))
            
        elif sse_type == 'b':  # Beta Sheet
            color = "#CFB53B"  # Gold
            width = 0.5 * self.coord_scale
            
            # Sheets are flat ribbons. We need to compute frames.
            # We use the _build_backbone_frames logic which takes 'point' and 'normal_hint'
            
            entries = [{"point": p, "normal_hint": h} for p, h in zip(points, normal_hints)]
            frames = self._build_backbone_frames(entries)
            
            ribbon_points = [f["point"] for f in frames]
            ribbon_normals = [f["normal"] for f in frames]
            
            self._make_strip(ribbon_points, ribbon_normals, group, color=color, width_scale=0.5)
            
        else:  # Coil
            color = "#9E9E9E"  # Grey
            radius = 0.06 * self.coord_scale
            group.add(self._create_smooth_tube(points, radius, color))


    def _parse_pdb_to_data(self):
        """Parse PDB file and convert to ChemObject3D data format."""
        parser = PDBParser(QUIET=True)

        try:
            structure = parser.get_structure("macromolecule", self.pdb_file)
        except Exception as e:
            raise ValueError(f"Failed to parse PDB file: {e}")
        
        atoms_data = []
        bonds_data = []
        
        # Map (chain_id, res_id, atom_name) -> linear_index
        atom_map = {}
        
        current_idx = 0
        
        # 1. Collect Atoms
        for model in structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        element = atom.element.upper().strip()
                        if not self.include_hydrogens and element == "H":
                            continue
                            
                        coords = atom.coord.tolist() # numpy array to list
                        
                        res_id = residue.id
                        # residue.id is usually (' ', 123, ' ') or ('W', 123, ' ') or ('H_LIG', 123, ' ')
                        hetero_flag = res_id[0].strip()
                        res_num = res_id[1]
                        ins_code = res_id[2].strip()

                        is_water = (hetero_flag == "W") or (residue.resname in ["HOH", "WAT"])
                        is_hetero = (hetero_flag != "") and (not is_water)

                        atom_info = {
                            "element": element,
                            "coords": coords,
                            "id": atom.serial_number,
                            "name": atom.name,
                            "residue_name": residue.resname,
                            "residue_number": res_num,
                            "insertion_code": ins_code,
                            "chain": chain.id,
                            "is_water": is_water,
                            "is_hetero": is_hetero
                        }
                        atoms_data.append(atom_info)
                        
                        # Store index for bond mapping
                        key = (chain.id, residue.id, atom.name)
                        atom_map[key] = current_idx
                        current_idx += 1
            break # Only parse the first model
            
        # 2. Infer Bonds (Distance based + Backbone logic)
        
        for model in structure:
            for chain in model:
                residues = list(chain)
                for i, residue in enumerate(residues):
                    
                    # A. Intra-residue bonds
                    res_atoms = []
                    for atom in residue:
                        if not self.include_hydrogens and atom.element.upper() == "H":
                            continue
                        key = (chain.id, residue.id, atom.name)
                        if key in atom_map:
                            res_atoms.append((atom, atom_map[key]))
                            
                    # Check distances N^2 within residue
                    for idx1, (a1, i1) in enumerate(res_atoms):
                        for idx2, (a2, i2) in enumerate(res_atoms):
                            if i1 >= i2: continue
                            
                            dist = a1 - a2 # Biopython atoms support subtraction
                            if dist < 1.7: # Covalent bond threshold
                                bonds_data.append({"aid1": i1+1, "aid2": i2+1, "order": 1})
                                
                    # B. Peptide Bond (to next residue)
                    if i < len(residues) - 1:
                        next_res = residues[i+1]
                        if "C" in residue and "N" in next_res:
                            c_atom = residue["C"]
                            n_atom = next_res["N"]
                            dist = c_atom - n_atom
                            if dist < 1.5:
                                k1 = (chain.id, residue.id, "C")
                                k2 = (chain.id, next_res.id, "N")
                                if k1 in atom_map and k2 in atom_map:
                                    bonds_data.append({
                                        "aid1": atom_map[k1]+1, 
                                        "aid2": atom_map[k2]+1, 
                                        "order": 1
                                    })
                                    
                    # C. Nucleic Acid Backbone (O3' -> P)
                    if i < len(residues) - 1:
                        next_res = residues[i+1]
                        o3_names = ["O3'", "O3*"]
                        o3_atom = None
                        for n in o3_names:
                            if n in residue:
                                o3_atom = residue[n]
                                break
                        
                
                        if o3_atom and "P" in next_res:
                            p_atom = next_res["P"]

                            dist = o3_atom - p_atom
                            if dist < 1.8:
                                k1 = (chain.id, residue.id, o3_atom.name)
                                k2 = (chain.id, next_res.id, "P")
                                if k1 in atom_map and k2 in atom_map:
                                    bonds_data.append({
                                        "aid1": atom_map[k1]+1, 
                                        "aid2": atom_map[k2]+1, 
                                        "order": 1
                                    })

                break # Only first model
        
        return {
            "atoms": atoms_data,
            "bonds": bonds_data
        }

    def _create_surface(self, style='gaussian', resolution=0.5):
        """Create a molecular surface mesh using Gaussian blobs and marching cubes."""
        if not SKIMAGE_AVAILABLE:
            print("Warning: scikit-image not installed. Cannot create Gaussian surface.")
            return Group()

        # 1. Collect atom coords and radii
        coords_list = []
        radii_list = []
        
        for atom_data in self.molecule_data["atoms"]:
            # Basic filter (e.g. ignore water for main surface? user preference)
            # Use 'show_water' logic if needed. Assuming surface creates main structure surface.
            if not self.show_water and atom_data.get("is_water", False):
                continue
            if not self.show_heteroatoms and atom_data.get("is_hetero", False):
                continue

            coords_list.append(atom_data["coords"])
            # Get VDW radius. Default 1.5 if missing.
            elem = atom_data["element"]
            # Minimal mapping or use get_element_data
            r = 1.5 
            if elem == "H": r = 1.1
            elif elem == "C": r = 1.7
            elif elem == "N": r = 1.55
            elif elem == "O": r = 1.52
            elif elem == "S": r = 1.8
            radii_list.append(r)

        if not coords_list:
            return Group()
            
        coords = np.array(coords_list)
        radii = np.array(radii_list)
        
        # Normalize coords relative to local system
        # Self must be initialized to have center_coords
        
        # 2. Define Grid
        padding = 3.0
        min_bounds = np.min(coords, axis=0) - padding
        max_bounds = np.max(coords, axis=0) + padding
        
        # grid resolution (Angstroms)
        res = resolution 
        
        dims = np.ceil((max_bounds - min_bounds) / res).astype(int)
        
        # Create grid
        # We accumulate density
        volume = np.zeros(dims)
        
        # 3. Rasterize Atoms (Gaussian)
        # Vectorized approach:
        
        grid_x = np.arange(dims[0]) * res + min_bounds[0]
        grid_y = np.arange(dims[1]) * res + min_bounds[1]
        grid_z = np.arange(dims[2]) * res + min_bounds[2]
        
        # Optimization: Only compute for atoms.
        cutoff = 2.5 # Sigma multiplier for bound
        
        for i, center in enumerate(coords):
            radius = radii[i]
            # Gaussian: exp( - (d/R)**2 ) 
            
            # Find subgrid
            sub_min = center - radius * cutoff
            sub_max = center + radius * cutoff
            
            idx_start = np.floor((sub_min - min_bounds) / res).astype(int)
            idx_end = np.ceil((sub_max - min_bounds) / res).astype(int) + 1
            
            idx_start = np.maximum(idx_start, 0)
            idx_end = np.minimum(idx_end, dims)
            
            if np.any(idx_start >= idx_end): continue
            
            # Local grid coords
            x_range = grid_x[idx_start[0]:idx_end[0]]
            y_range = grid_y[idx_start[1]:idx_end[1]]
            z_range = grid_z[idx_start[2]:idx_end[2]]
            
            # We need to broadcast properly. 
            # meshgrid ij is good.
            # But creating meshgrid for every atom is slow?
            # Actually, (dx)**2 + (dy)**2 + (dz)**2 is faster if done with broadcasting without meshgrid maybe?
            # dist_sq = (X-xc)**2 + ...
            # X shape is (N,1,1), Y is (1,M,1), Z is (1,1,K)
            
            X_local = x_range[:, None, None]
            Y_local = y_range[None, :, None]
            Z_local = z_range[None, None, :]
            
            dist_sq = (X_local - center[0])**2 + (Y_local - center[1])**2 + (Z_local - center[2])**2
            
            # Calibrate so that value is 0.5 at dist = radius
            # exp( - coeff * (d/R)^2 ) = 0.5 => -coeff = ln(0.5) => coeff = 0.693
            blob = np.exp( - 0.693 * dist_sq / (radius**2) ) 
            
            volume[idx_start[0]:idx_end[0], idx_start[1]:idx_end[1], idx_start[2]:idx_end[2]] += blob
            
            
        # 4. Marching Cubes
        threshold = 0.5 
        
        try:
            verts, faces, normals, values = measure.marching_cubes(volume, level=threshold)
        except Exception as e:
            print(f"Marching Cubes failed: {e}")
            return Group()
        
        # 5. Build Mesh
        real_verts = verts * res + min_bounds
        
        # Normalize
        raw_mean = np.mean(coords, axis=0) if self.center_coords is None else self.center_coords
        norm_verts = (real_verts - raw_mean) * self.coord_scale
        
        surface_group = Group()
        
        # Optimize: Batch polygons? 
        # ManimGL VGroup is fast.
        
        surf_color = "#2E8B57" # SeaGreen
        
        # Helper for color interpolation (in case not in scope)
        def h2r(hex_col):
            if hex_col.startswith("#"): hex_col = hex_col[1:]
            return np.array([int(hex_col[i:i+2], 16) for i in (0, 2, 4)]) / 255.0
            
        def r2h(rgb):
            return "#" + "".join([f"{int(c*255):02x}" for c in np.clip(rgb, 0, 1)])
            
        base_rgb = h2r(surf_color)
        light_dir = np.array([0.5, 0.5, 1.0])
        light_dir /= np.linalg.norm(light_dir)
        
        # Use vertex normals from marching cubes for smoother shading
        # 'normals' output is per-vertex. We'll average for each face.
        # norm_verts are transformed, but normals should remain in original orientation (just need to match scale)
        
        for i, face in enumerate(faces):
             pts = norm_verts[face]
             
             # Average vertex normals for the face (smoother than face normal)
             face_normal = np.mean(normals[face], axis=0)
             norm_len = np.linalg.norm(face_normal)
             if norm_len > 0:
                 face_normal /= norm_len
             else:
                 face_normal = np.array([0, 0, 1])
                 
             # Lambertian diffuse
             diffuse = np.clip(np.dot(face_normal, light_dir), 0, 1)
             
             # Simple specular (Blinn-Phong style) for highlights
             view_dir = np.array([0, 0, 1])  # Assume camera looking from +Z
             half_vec = light_dir + view_dir
             half_vec /= np.linalg.norm(half_vec)
             specular = np.clip(np.dot(face_normal, half_vec), 0, 1) ** 32  # Shininess
             
             # Combine: ambient + diffuse + specular
             intensity = 0.15 + 0.65 * diffuse + 0.2 * specular
             
             shaded_rgb = base_rgb * intensity
             shaded_hex = r2h(shaded_rgb)
             
             poly = Polygon(*pts, color=shaded_hex, fill_opacity=1, stroke_width=0, stroke_opacity=0)
             surface_group.add(poly)
             
        return surface_group


    @classmethod
    def from_pdb_id(cls, pdb_id, download_dir=None, **kwargs):
        """
        Fetches a PDB file from RCSB and creates a Macromolecule.
        pdb_id: The 4-character PDB ID (e.g., '1CRN').
        download_dir: Optional directory to save the downloaded file.
        """
        from .connect import fetch_pdb_file
        
        filename = fetch_pdb_file(pdb_id, download_dir=download_dir)
        if not filename:
            raise ValueError(f"Could not fetch PDB file for ID: {pdb_id}")
            
        return cls(filename, **kwargs)
