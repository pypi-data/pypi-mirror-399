from manimlib import *
import numpy as np

class ChemObject(VGroup):
    """
    Chemical structure visualization using 2D line structure.
    Supports VSEPR (default), straight_chain, zigzag_chain, and skeletal modes.
    """
    
    STANDARD_BOND_LENGTH = 1.5
    
    def __init__(self, molecule_data=None, font_size=32, bond_stroke=4, bond_length=None, 
                 straight_chain=False, zigzag_chain=False, skeletal=False,
                 use_external_coords=True, skeletal_carbon_marker_radius=0.0,
                 skeletal_carbon_marker_color=WHITE, lock_text_to_view=True, **kwargs):
        super().__init__(**kwargs)
        
        self.font_size = font_size
        self.bond_stroke = bond_stroke
        self.bond_length = bond_length or self.STANDARD_BOND_LENGTH
        self.straight_chain = straight_chain
        self.zigzag_chain = zigzag_chain
        self.skeletal = skeletal
        # When True and coordinate data is provided (e.g., from RDKit), use it instead of regenerating.
        self.use_external_coords = use_external_coords
        self.skeletal_carbon_marker_radius = skeletal_carbon_marker_radius
        self.skeletal_carbon_marker_color = skeletal_carbon_marker_color
        self.lock_text_to_view = lock_text_to_view
        
        self.molecule_data = molecule_data
        self.atoms_dict = {}
        self.atoms_group = VGroup()
        self.bonds_group = VGroup()
        self.bond_dict = {}
        self.adjacency = {}
        self.lone_pairs_group = VGroup()

        if molecule_data:
            self._build_molecule()

    def _build_molecule(self):
        data = self.molecule_data
        if not data:
            return
            
        atoms_data = data.get('atoms', [])
        bonds_data = data.get('bonds', [])
        
        if not atoms_data:
            return
        
        n = len(atoms_data)
        adjacency = {i: [] for i in range(n)}
        for b in bonds_data:
            i, j = b['aid1'] - 1, b['aid2'] - 1
            if 0 <= i < n and 0 <= j < n:
                adjacency[i].append((j, b.get('order', 1)))
                adjacency[j].append((i, b.get('order', 1)))

        self.adjacency = adjacency
        
        symbols = [self._get_symbol(a.get('element')) for a in atoms_data]

        # Try to inject RDKit 2D coords if available and allowed (e.g., fetched from PubChem but missing coords)
        if self.use_external_coords and not all('coords' in a for a in atoms_data):
            smiles = data.get('smiles')
            if smiles:
                try:
                    from .rdkit_adapter import compute_rdkit_2d_coords
                    rdkit_coords, rdkit_symbols = compute_rdkit_2d_coords(smiles, add_h=False)
                    if len(rdkit_coords) == len(atoms_data) and rdkit_symbols == symbols:
                        for atom_info, rc in zip(atoms_data, rdkit_coords):
                            atom_info['coords'] = rc
                except Exception:
                    pass  # Optional dependency; silently fall back to internal layout

        # If explicit coordinates are provided (e.g., from RDKit) and allowed, honor them; otherwise generate.
        if self.use_external_coords and all('coords' in a for a in atoms_data):
            coords = np.array([a['coords'] for a in atoms_data], dtype=float)
        else:
            coords = self._generate_coords(symbols, adjacency)
        
        for i, atom_info in enumerate(atoms_data):
            symbol = symbols[i]

            # Skip hydrogens entirely in skeletal mode
            if self.skeletal and symbol == 'H':
                continue

            if self.skeletal and symbol == 'C':
                atom_mob = VectorizedPoint(coords[i]).set_z_index(1)
                atom_mob.symbol = symbol
                atom_mob.is_skeletal_placeholder = True
                if self.skeletal_carbon_marker_radius > 0:
                    marker = Dot(
                        point=coords[i],
                        radius=self.skeletal_carbon_marker_radius,
                        color=self.skeletal_carbon_marker_color,
                        fill_opacity=1.0,
                        stroke_width=0,
                    ).set_z_index(2)
                    # Keep marker in atoms_group for easy styling/animations
                    marker.symbol = symbol
                    marker.is_skeletal_marker = True
                    self.atoms_group.add(marker)
            else:
                atom_mob = Text(symbol, font_size=self.font_size).set_z_index(2)
                atom_mob.symbol = symbol
                atom_mob.is_skeletal_placeholder = False
            atom_mob.move_to(coords[i])
            
            # Handle charge
            charge = atom_info.get('charge', 0)
            if charge != 0:
                sign = '+' if charge > 0 else '-'
                val = str(abs(charge)) if abs(charge) > 1 else ""
                charge_str = f"{val}{sign}"
                charge_mob = Text(charge_str, font_size=self.font_size * 0.6).set_color(WHITE)
                
                # Position superscript
                if isinstance(atom_mob, VectorizedPoint):
                     charge_mob.next_to(atom_mob, UP+RIGHT, buff=0.1)
                else:
                     # Place relative to symbol
                     # Move to corner then shift a bit
                     charge_mob.move_to(atom_mob.get_corner(UP+RIGHT) + np.array([charge_mob.width/2, charge_mob.height/3, 0]))
                
                self.atoms_group.add(charge_mob)
                atom_mob.charge_label = charge_mob
                
                if self.lock_text_to_view:
                    # Provide metadata for rotation handling
                    atom_mob.is_labeled_atom = True
                    if hasattr(atom_mob, "charge_label"):
                         atom_mob.charge_label.is_charge_label = True

            self.atoms_dict[i] = atom_mob
            self.atoms_group.add(atom_mob)
            
            # (Rotation locking handled in overridden rotate method)
        
        for b in bonds_data:
            idx1, idx2 = b['aid1'] - 1, b['aid2'] - 1
            order = b.get('order', 1)
            if idx1 in self.atoms_dict and idx2 in self.atoms_dict:
                bond_mob = self._create_bond(idx1, idx2, order)
                # Attach metadata so users can address bonds directly.
                bond_mob.aid1 = idx1
                bond_mob.aid2 = idx2
                bond_mob.order = order
                self.bonds_group.add(bond_mob)
                self.bond_dict[tuple(sorted((idx1, idx2)))] = bond_mob
        
        self.add(self.bonds_group, self.atoms_group, self.lone_pairs_group)

    def _generate_coords(self, symbols, adjacency):
        n = len(symbols)
        coords = np.zeros((n, 3))
        placed = [False] * n
        
        if n == 0:
            return coords

        placed_count = 0
        current_x_left = 0.0

        while placed_count < n:
            # 1. Pick a start node for a new component (prefer heavy)
            unplaced = [i for i in range(n) if not placed[i]]
            if not unplaced: break
            
            heavy_unplaced = [i for i in unplaced if symbols[i] != 'H']
            start_node = heavy_unplaced[0] if heavy_unplaced else unplaced[0]
            
            # 2. Identify component nodes
            component_nodes = set()
            stack = [start_node]
            while stack:
                curr = stack.pop()
                if curr in component_nodes: continue
                component_nodes.add(curr)
                for nb, _ in adjacency[curr]:
                    if nb not in component_nodes:
                        stack.append(nb)
            component_list = list(component_nodes)
            
            # 3. Layout this component
            # We work with relative coordinates first (centered at 0 locally)
            
            comp_heavy = [i for i in component_list if symbols[i] != 'H']
            
            # Backbone / Chain Logic
            if (self.straight_chain or self.zigzag_chain) and comp_heavy:
                # Build heavy adjacency for this component
                comp_heavy_adj = {i: [] for i in comp_heavy}
                for i in comp_heavy:
                    for nb, order in adjacency[i]:
                        if symbols[nb] != 'H':
                            comp_heavy_adj[i].append(nb)
                
                terminals = [i for i in comp_heavy if len(comp_heavy_adj[i]) <= 1]
                bb_start = terminals[0] if terminals else comp_heavy[0]
                backbone = self._find_backbone(bb_start, comp_heavy_adj)
                
                theta = np.deg2rad(30)
                coords[backbone[0]] = np.array([0, 0, 0])
                placed[backbone[0]] = True
                
                for idx, atom_idx in enumerate(backbone[1:], start=1):
                    if self.zigzag_chain:
                        sign = 1 if idx % 2 == 1 else -1
                        step = np.array([
                            np.cos(theta) * self.bond_length,
                            sign * np.sin(theta) * self.bond_length,
                            0
                        ])
                        coords[atom_idx] = coords[backbone[idx - 1]] + step
                    else:
                        coords[atom_idx] = coords[backbone[idx - 1]] + np.array([self.bond_length, 0, 0])
                    placed[atom_idx] = True
                    
                # Place H atoms on backbone
                for atom_idx in backbone:
                    neighbors = adjacency[atom_idx]
                    h_neighbors = [nb for nb, _ in neighbors if symbols[nb] == 'H' and not placed[nb]]
                    if not h_neighbors: continue
                    
                    backbone_angles = []
                    for nb, _ in neighbors:
                        if placed[nb] and symbols[nb] != 'H':
                            vec = coords[nb] - coords[atom_idx]
                            if np.linalg.norm(vec) > 0:
                                backbone_angles.append(np.arctan2(vec[1], vec[0]))
                    
                    if self.zigzag_chain:
                        if len(backbone_angles) == 1:
                            chain_angle = backbone_angles[0]
                            opposite = chain_angle + np.pi
                            available = [opposite, np.pi/2, -np.pi/2]
                        else:
                            available = [np.pi/2, -np.pi/2]
                    else:
                        available = [np.pi/2, -np.pi/2, np.pi, 0]
                    
                    # Filter used directions
                    all_used = []
                    for nb, _ in neighbors:
                        if placed[nb]:
                            vec = coords[nb] - coords[atom_idx]
                            if np.linalg.norm(vec) > 0:
                                all_used.append(np.arctan2(vec[1], vec[0]))
                    
                    free_angles = []
                    for a in available:
                        is_free = True
                        for used in all_used:
                            if abs(self._angle_diff(a, used)) < np.pi/3: # Looser tolerance
                                is_free = False
                                break
                        if is_free:
                            free_angles.append(a)
                    
                    if not free_angles:
                        free_angles = [np.pi/2, -np.pi/2, np.pi, 0]
                        
                    for i, nb in enumerate(h_neighbors):
                        if i < len(free_angles):
                            angle = free_angles[i]
                        else:
                            angle = free_angles[-1] + (i - len(free_angles) + 1) * np.pi/3
                        
                        coords[nb] = coords[atom_idx] + np.array([
                            np.cos(angle) * self.bond_length,
                            np.sin(angle) * self.bond_length,
                            0
                        ])
                        placed[nb] = True
                
                # BFS for remaining branches off the backbone
                queue = list(backbone)
                while queue:
                    current = queue.pop(0)
                    if current not in component_nodes: continue
                    
                    unplaced_nb = [nb for nb, o in adjacency[current] if not placed[nb]]
                    if not unplaced_nb: continue
                    
                    # Incoming direction
                    placed_nbs = [nb for nb, o in adjacency[current] if placed[nb]]
                    incoming_angle = 0
                    if placed_nbs:
                         v = coords[current] - coords[placed_nbs[0]]
                         incoming_angle = np.arctan2(v[1], v[0])
                    
                    for i, nb in enumerate(unplaced_nb):
                         if self.zigzag_chain:
                              # Try to continue zigzag roughly
                              # Just simple 60 degree turn
                              angle = incoming_angle + np.pi/3 * (1 if i % 2 == 0 else -1)
                         else:
                              # Straight -> perpendicular
                              angle = incoming_angle + np.pi/2 * (1 if i % 2 == 0 else -1)
                         
                         coords[nb] = coords[current] + np.array([
                             np.cos(angle) * self.bond_length,
                             np.sin(angle) * self.bond_length,
                             0
                         ])
                         placed[nb] = True
                         queue.append(nb)
            else:
                # VSEPR Logic for component
                central = max(component_list, key=lambda i: len(adjacency[i]))
                if comp_heavy:
                     central = max(comp_heavy, key=lambda i: len(adjacency[i]))
                
                coords[central] = np.array([0, 0, 0])
                placed[central] = True
                
                neighbors = adjacency[central]
                central_symbol = symbols[central]
                num_neighbors = len(neighbors)
                
                if num_neighbors == 2:
                    if central_symbol in ['O', 'S']:
                        half = 52.25 * np.pi / 180
                        angles = [np.pi/2 + half, np.pi/2 - half]
                    elif central_symbol == 'N':
                         half = 53.5 * np.pi / 180
                         angles = [np.pi/2 + half, np.pi/2 - half]
                    else:
                        angles = [0, np.pi]
                elif num_neighbors == 3:
                    angles = [np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 - 2*np.pi/3]
                elif num_neighbors == 4:
                    angles = [np.pi/2, -np.pi/2, 0, np.pi]
                else:
                    angles = [i * 2*np.pi / max(1, num_neighbors) for i in range(num_neighbors)]
                
                # Place neighbors of central
                for i, (nb, order) in enumerate(neighbors):
                     # Simple placement for central neighbors
                     # Note: logic for rotation/alignment (lines 309-311 of original) needed for BFS step
                     if i < len(angles):
                         angle = angles[i]
                     else:
                         angle = i * 2*np.pi / num_neighbors
                     coords[nb] = coords[central] + np.array([
                         np.cos(angle) * self.bond_length,
                         np.sin(angle) * self.bond_length,
                         0
                     ])
                     placed[nb] = True
                
                # BFS for remaining in component
                queue = [nb for nb, _ in neighbors] # seed with central's neighbors
                while queue:
                    current = queue.pop(0)
                    if current not in component_nodes: continue # Should be in component
                    
                    unplaced_nb = [(nb, o) for nb, o in adjacency[current] if not placed[nb]]
                    if not unplaced_nb: continue
                    
                    placed_nb_list = [nb for nb, o in adjacency[current] if placed[nb]]
                    incoming_angle = 0
                    if placed_nb_list:
                        vec = coords[current] - coords[placed_nb_list[0]]
                        incoming_angle = np.arctan2(vec[1], vec[0])
                    
                    for i, (nb, o) in enumerate(unplaced_nb):
                         angle = incoming_angle + np.pi/3 * (1 if i % 2 == 0 else -1)
                         coords[nb] = coords[current] + np.array([
                             np.cos(angle) * self.bond_length,
                             np.sin(angle) * self.bond_length,
                             0
                         ])
                         placed[nb] = True
                         queue.append(nb)

            # 4. Offset this component
            comp_indices = list(component_nodes)
            comp_coords = coords[comp_indices]
            min_x = np.min(comp_coords[:, 0])
            max_x = np.max(comp_coords[:, 0])
            
            # Shift so left edge is at current_x_left
            shift_x = current_x_left - min_x
            
            # Also center Y roughly? Let's align centroids vertically to 0?
            # Or assume 0,0,0 start was good.
            # Align centers vertically is usually good for simple ions (Na+ Cl-)
            center_y = np.mean(comp_coords[:, 1])
            shift_y = -center_y
            
            coords[comp_indices] += np.array([shift_x, shift_y, 0])
            
            current_x_left += (max_x - min_x) + (self.bond_length * 1.5)
            placed_count += len(component_nodes)
            
        # Center the whole assembly
        final_center = np.mean(coords, axis=0)
        coords -= final_center
        return coords

    def _find_backbone(self, start, heavy_adj):
        """Find longest path from start in heavy atom graph."""
        visited = set()
        path = []
        
        def dfs(node, current_path):
            nonlocal path
            visited.add(node)
            current_path.append(node)
            
            if len(current_path) > len(path):
                path = current_path.copy()
            
            for nb in heavy_adj.get(node, []):
                if nb not in visited:
                    dfs(nb, current_path)
            
            current_path.pop()
            visited.remove(node)
        
        dfs(start, [])
        return path

    def _angle_diff(self, a1, a2):
        diff = a1 - a2
        while diff > np.pi: diff -= 2*np.pi
        while diff < -np.pi: diff += 2*np.pi
        return abs(diff)

    def _get_symbol(self, element):
        from .data import PERIODIC_TABLE
        if isinstance(element, str) and not element.isdigit():
            return element
        try:
            num = int(element)
            if num in PERIODIC_TABLE:
                return PERIODIC_TABLE[num]['symbol']
        except (ValueError, TypeError):
            pass
        return str(element)

    def _atom_edge_offset(self, atom_mob, direction):
        """Distance from an atom center to the text edge along a direction."""
        if self.skeletal and getattr(atom_mob, "is_skeletal_placeholder", False):
            return 0.0

        direction = np.array(direction, dtype=float)
        norm = np.linalg.norm(direction[:2])
        if norm == 0:
            return 0.0
        unit = direction / norm
        width, height = atom_mob.width, atom_mob.height
        projected = 0.5 * (abs(unit[0]) * width + abs(unit[1]) * height)
        gap = max(0.05, min(0.2 * self.bond_length, 0.25 * atom_mob.height))
        return projected + gap

    def _bond_endpoints(self, atom1, atom2):
        start, end = atom1.get_center(), atom2.get_center()
        vector = end - start
        length = np.linalg.norm(vector)
        if length == 0:
            return start, end

        unit = vector / length
        start_trim = self._atom_edge_offset(atom1, unit)
        end_trim = self._atom_edge_offset(atom2, -unit)
        total_trim = start_trim + end_trim

        # Keep a visible bond even when atoms are close
        max_trim = length * 0.8
        if total_trim > max_trim:
            scale = max_trim / total_trim
            start_trim *= scale
            end_trim *= scale

        return start + unit * start_trim, end - unit * end_trim

    def _create_bond(self, idx1, idx2, order):
        atom1, atom2 = self.atoms_dict[idx1], self.atoms_dict[idx2]
        start, end = self._bond_endpoints(atom1, atom2)

        if order == 1:
            return Line(start, end, stroke_width=self.bond_stroke)
        elif order == 2:
            return self._create_double_bond(start, end)
        elif order == 3:
            return self._create_triple_bond(start, end)
        return Line(start, end, stroke_width=self.bond_stroke)

    def _create_double_bond(self, start, end):
        v = end - start
        length = np.linalg.norm(v)
        if length == 0: return VGroup()
        unit_v, normal = v/length, np.array([-v[1]/length, v[0]/length, 0])
        offset = 0.08

        if self.skeletal:
            # Keep the main stroke centered so side single bonds meet cleanly; offset only the second line
            return VGroup(
                Line(start, end, stroke_width=self.bond_stroke),
                Line(start + normal*offset, end + normal*offset, stroke_width=self.bond_stroke)
            )

        return VGroup(
            Line(start + normal*offset, end + normal*offset, stroke_width=self.bond_stroke),
            Line(start - normal*offset, end - normal*offset, stroke_width=self.bond_stroke)
        )

    def _create_triple_bond(self, start, end):
        v = end - start
        length = np.linalg.norm(v)
        if length == 0: return VGroup()
        unit_v, normal = v/length, np.array([-v[1]/length, v[0]/length, 0])
        offset = 0.1

        if self.skeletal:
            # Central line stays aligned with adjoining single bonds; flank lines offset equally
            return VGroup(
                Line(start, end, stroke_width=self.bond_stroke),
                Line(start + normal*offset, end + normal*offset, stroke_width=self.bond_stroke),
                Line(start - normal*offset, end - normal*offset, stroke_width=self.bond_stroke)
            )

        return VGroup(
            Line(start, end, stroke_width=self.bond_stroke),
            Line(start + normal*offset, end + normal*offset, stroke_width=self.bond_stroke),
            Line(start - normal*offset, end - normal*offset, stroke_width=self.bond_stroke)
        )

    # --- Public helpers for user-driven atom/bond transforms ---
    def get_atom(self, idx):
        return self.atoms_dict.get(idx)

    def get_bond(self, aid1, aid2):
        return self.bond_dict.get(tuple(sorted((aid1, aid2))))

    def iter_atoms(self):
        return list(self.atoms_dict.items())

    def iter_bonds(self):
        return list(self.bond_dict.items())

    def animate_atom_to(self, idx, point):
        atom = self.get_atom(idx)
        if not atom:
            return AnimationGroup()
        return atom.animate.move_to(point)

    def enable_dynamic_bonds(self):
        """Attach updaters so bonds follow atoms during user-driven transforms."""
        for (i, j), bond_mob in self.bond_dict.items():
            self._attach_bond_updater(bond_mob, i, j)
        return self

    def _attach_bond_updater(self, bond_mob, idx1, idx2):
        def get_endpoints():
            a1, a2 = self.atoms_dict.get(idx1), self.atoms_dict.get(idx2)
            if not a1 or not a2:
                return None, None
            return self._bond_endpoints(a1, a2)

        order = getattr(bond_mob, "order", 1)

        if order == 1 and isinstance(bond_mob, Line):
            def upd(m):
                start, end = get_endpoints()
                if start is None:
                    return m
                m.put_start_and_end_on(start, end)
                return m
            bond_mob.add_updater(upd)
            return

        def multi_updater(mobj, order_val):
            start, end = get_endpoints()
            if start is None:
                return mobj
            v = end - start
            length = np.linalg.norm(v)
            if length == 0:
                return mobj
            normal = np.array([-v[1]/length, v[0]/length, 0])
            if order_val == 2:
                offset = 0.08
                if self.skeletal:
                    lines = mobj.submobjects
                    if len(lines) >= 1:
                        lines[0].put_start_and_end_on(start, end)
                    if len(lines) >= 2:
                        lines[1].put_start_and_end_on(start + normal*offset, end + normal*offset)
                else:
                    lines = mobj.submobjects
                    if len(lines) >= 1:
                        lines[0].put_start_and_end_on(start + normal*offset, end + normal*offset)
                    if len(lines) >= 2:
                        lines[1].put_start_and_end_on(start - normal*offset, end - normal*offset)
            elif order_val == 3:
                offset = 0.1
                lines = mobj.submobjects
                if len(lines) >= 1:
                    lines[0].put_start_and_end_on(start, end)
                if len(lines) >= 2:
                    lines[1].put_start_and_end_on(start + normal*offset, end + normal*offset)
                if len(lines) >= 3:
                    lines[2].put_start_and_end_on(start - normal*offset, end - normal*offset)
            return mobj

        if isinstance(bond_mob, VGroup):
            bond_mob.add_updater(lambda m: multi_updater(m, order))

    # --- End public helpers ---

    def add_functional_group_highlights(
        self,
        matches,
        palette=None,
        label_font_size=None,
        fill_opacity=0.08,
        stroke_width=3,
        buff=None,
        show_labels=True,
    ):
        """Draw rounded boxes and labels over detected functional groups."""
        if palette is None:
            try:
                from .rdkit_adapter import functional_group_palette
                palette = functional_group_palette()
            except Exception:
                palette = {"default": WHITE}

        label_font_size = label_font_size or max(18, int(self.font_size * 0.7))
        pad = buff if buff is not None else self.bond_length * 0.6

        overlays = VGroup()
        for match in matches:
            indices = match.get("atom_indices") or []
            atoms = [self.atoms_dict[i] for i in indices if i in self.atoms_dict]
            if not atoms:
                continue

            centers = np.array([a.get_center() for a in atoms])
            min_pt, max_pt = centers.min(axis=0), centers.max(axis=0)
            width, height = (max_pt - min_pt)[:2] + pad
            color = palette.get(match.get("category")) or palette.get("default") or WHITE

            rect = RoundedRectangle(
                width=max(width, self.bond_length * 0.8),
                height=max(height, self.bond_length * 0.6),
                corner_radius=0.15 * self.bond_length,
                stroke_color=color,
                stroke_width=stroke_width,
                fill_color=color,
                fill_opacity=fill_opacity,
            )
            rect.move_to((min_pt + max_pt) / 2)
            overlays.add(rect)

            if show_labels:
                label_text = match.get("label") or match.get("key") or "fg"
                label = Text(label_text, font_size=label_font_size, color=color)
                label.next_to(rect, UP, buff=0.15 * self.bond_length)
                overlays.add(label)

        self.add(overlays)
        return overlays

    def add_lone_pairs(
        self,
        lone_pairs_map,
        radius=0.05,
        distance=None,
        color=YELLOW,
        dot_separation=None,
    ):
        """Render lone-pair electron dots around specified atoms.

        lone_pairs_map: dict of atom_index -> number of lone pairs (int)
        radius: dot radius
        distance: radial distance from atom center (defaults to ~0.35 * bond_length)
        color: dot color
        dot_separation: separation between the two dots in a pair (defaults to 2*radius)
        """

        distance = distance or self.bond_length * 0.35
        dot_separation = dot_separation or radius * 2.0

        overlays = VGroup()

        def neighbor_mean_direction(idx):
            nbs = self.adjacency.get(idx, []) if hasattr(self, "adjacency") else []
            if not nbs:
                return np.array([1.0, 0.0, 0.0])
            center = self.atoms_dict[idx].get_center()
            vecs = []
            for nb, _ in nbs:
                if nb in self.atoms_dict:
                    vecs.append(self.atoms_dict[nb].get_center() - center)
            if not vecs:
                return np.array([1.0, 0.0, 0.0])
            mean_vec = np.mean(vecs, axis=0)
            norm = np.linalg.norm(mean_vec)
            if norm < 1e-6:
                return np.array([1.0, 0.0, 0.0])
            return -mean_vec / norm  # point away from neighbors

        for idx, pair_count in (lone_pairs_map or {}).items():
            if pair_count <= 0:
                continue
            atom = self.atoms_dict.get(idx)
            if not atom:
                continue

            base_dir = neighbor_mean_direction(idx)
            base_angle = np.arctan2(base_dir[1], base_dir[0])
            step = 2 * np.pi / max(pair_count, 1)

            for k in range(pair_count):
                angle = base_angle + k * step
                dir_vec = np.array([np.cos(angle), np.sin(angle), 0])
                perp = np.array([-dir_vec[1], dir_vec[0], 0])

                center_pos = atom.get_center() + dir_vec * distance
                dot_offset = perp * (dot_separation / 2.0)

                d1 = Dot(radius=radius, color=color, fill_color=color, fill_opacity=1.0)
                d2 = Dot(radius=radius, color=color, fill_color=color, fill_opacity=1.0)
                d1.move_to(center_pos + dot_offset)
                d2.move_to(center_pos - dot_offset)

                overlays.add(d1, d2)

        self.lone_pairs_group.add(overlays)
        self.add(overlays)
        return overlays

    def rotate(self, angle, axis=OUT, **kwargs):
        """
        Rotates the ChemObject. Uses super().rotate but handles text locking if enabled.
        """
        super().rotate(angle, axis=axis, **kwargs)
        
        # If locking is enabled and rotation is around Z-axis (2D rotation)
        if getattr(self, "lock_text_to_view", True) and np.allclose(axis, OUT):
            for mob in self.atoms_group:
                # If it's a Text object (atom symbol) or has explicit flag
                is_text = isinstance(mob, Text)
                # Check for explicit flags we set before
                is_labeled = getattr(mob, "is_labeled_atom", False)
                
                if is_text or is_labeled:
                     # Counter-rotate the atom text about its own center
                     mob.rotate(-angle, axis=axis, about_point=mob.get_center())
                     
                     # Also handle charge label if present
                     if hasattr(mob, "charge_label"):
                          # We need to rotate the charge label about its center to keep it upright
                          # AND rotate its position around the atom center? 
                          # Actually, if we rotated super(), everything moved properly.
                          # The charge label geometry rotated relative to atom center.
                          # But the text itself is now tilted.
                          # So we just counter-rotate the text about its OWN center.
                          mob.charge_label.rotate(-angle, axis=axis, about_point=mob.charge_label.get_center())
        return self

    def mirror_horizontal(self, rotate_text=False):
        self.flip(axis=UP)
        if not rotate_text:
            for a in self.atoms_group: a.flip(axis=UP, about_point=a.get_center())
        return self

    def mirror_vertical(self, rotate_text=False):
        self.flip(axis=RIGHT)
        if not rotate_text:
            for a in self.atoms_group: a.flip(axis=RIGHT, about_point=a.get_center())
        return self

    def rotate_molecule(self, angle, axis=OUT, about_point=None, rotate_text=False):
        # Now delegates to self.rotate which handles locking automatically if configured.
        # But if rotate_text is explicitly passed, we might need to respect it?
        # Let's just use self.rotate. The 'rotate_text' param here is legacy manual control.
        # If user explicitly asks NOT to rotate text (rotate_text=False), our lock logic handles it.
        # If user DOES want to rotate text (rotate_text=True), we might need to temporarily disable lock?
        
        # For backward compat / explicit control:
        if rotate_text:
             # Force rotation of text by temporarily disabling lock
             old_lock = self.lock_text_to_view
             self.lock_text_to_view = False
             self.rotate(angle, axis=axis, about_point=about_point)
             self.lock_text_to_view = old_lock
        else:
             # Default behavior (uses lock settings)
             self.rotate(angle, axis=axis, about_point=about_point)
        return self

    def break_bond(self, a1, a2):
        key = tuple(sorted((a1, a2)))
        if key in self.bond_dict:
            b = self.bond_dict.pop(key)
            self.bonds_group.remove(b)
            return Uncreate(b)
        return AnimationGroup()

    def form_bond(self, a1, a2, order=1):
        key = tuple(sorted((a1, a2)))
        if key in self.bond_dict or a1 not in self.atoms_dict or a2 not in self.atoms_dict:
            return AnimationGroup()
        b = self._create_bond(a1, a2, order)
        self.bonds_group.add(b)
        self.bond_dict[key] = b
        return Create(b)

    @classmethod
    def from_file(cls, filepath, **kwargs):
        import json
        from .connect import parse_pubchem_json
        with open(filepath, 'r') as f:
            data = json.load(f)
        parsed = parse_pubchem_json(data)
        if not parsed:
            raise ValueError(f"Could not parse {filepath}")
        return cls(parsed, **kwargs)

    @classmethod
    def from_pubchem(cls, identifier, **kwargs):
        from .connect import fetch_molecule_data
        data = fetch_molecule_data(identifier)
        if not data:
            raise ValueError(f"Could not fetch {identifier}")
        return cls(data, **kwargs)

    @classmethod
    def from_smiles_rdkit(cls, smiles, add_h=False, **kwargs):
        """
        Build ChemObject from a SMILES string using RDKit for coordinates.

        RDKit is an optional dependency; raises ImportError with guidance if missing.
        """
        from .rdkit_adapter import molecule_data_from_smiles

        data = molecule_data_from_smiles(smiles, add_h=add_h)
        return cls(data, **kwargs)


CObject = ChemObject
