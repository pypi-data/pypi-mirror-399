import pubchempy as pcp

def fetch_molecule_data(identifier):
    """
    Fetches molecule data from PubChem.
    identifier: Name (str) or CID (int)
    """
    try:
        if isinstance(identifier, int):
            c = pcp.Compound.from_cid(identifier)
        else:
            c = pcp.get_compounds(identifier, 'name', record_type='3d')
            if not c:
                # Try 2d if 3d not available
                c = pcp.get_compounds(identifier, 'name')
            
            if c:
                c = c[0]
            else:
                return None

        # Get details
        # Note: obtaining 2D/3D coords requires specific request or parsed atom property
        # PubChemPy 'atoms' property has coordinates if fetched with record_type='3d'
        
        atoms = []
        coords = []
        for atom in c.atoms:
            coord = None
            if atom.x is not None and atom.y is not None:
                # Z might be None for 2D
                z = atom.z if atom.z is not None else 0.0
                coord = [atom.x, atom.y, z]
                coords.append(coord)

            atom_rec = {'element': atom.element, 'aid': atom.aid}
            if coord is not None:
                atom_rec['coords'] = coord
            atoms.append(atom_rec)
        
        bonds = []
        for bond in c.bonds:
            bonds.append({'aid1': bond.aid1, 'aid2': bond.aid2, 'order': bond.order})

        # PubChem Atom IDs (aid) are usually 1-indexed and might not match list index exactly 1-to-1 if sorted differently?
        # Actually PubChemPy atoms list usually corresponds to simple indexing but let's be careful.
        # For simplicity in this demo, we assume the list order is the index order (0 to N-1).
        # We need to map aid to list index.
        aid_to_idx = {a['aid']: i for i, a in enumerate(atoms)}

        remapped_bonds = []
        for b in bonds:
            if b['aid1'] in aid_to_idx and b['aid2'] in aid_to_idx:
                remapped_bonds.append({
                    'aid1': aid_to_idx[b['aid1']] + 1, # Keep logic in core.py compatible (it does -1)
                    'aid2': aid_to_idx[b['aid2']] + 1,
                    'order': b['order']
                })

        # Attach coordinates to atoms when available so downstream builders can reuse them directly.
        if coords and len(coords) == len(atoms):
            for atom, coord in zip(atoms, coords):
                atom.setdefault('coords', coord)

        dimensionality = 3 if any(len(c) > 2 and abs(c[2]) > 1e-6 for c in coords) else 2
        
        return {
            'atoms': atoms,
            'bonds': remapped_bonds,
            'coords': coords,
            'dimensionality': dimensionality,
            'smiles': getattr(c, 'isomeric_smiles', None) or getattr(c, 'canonical_smiles', None),
            'inchi': getattr(c, 'inchi', None),
            'molecular_formula': getattr(c, 'molecular_formula', None),
            'molecular_weight': getattr(c, 'molecular_weight', None),
            'cid': getattr(c, 'cid', None),
            'name': getattr(c, 'iupac_name', None) or getattr(c, 'title', None) or str(identifier),
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def parse_pubchem_json(data):
    """
    Parses a dictionary in PubChem JSON format (PC_Compounds).
    Returns the dict structure expected by Molecule.
    """
    try:
        if "PC_Compounds" in data:
            compound = data["PC_Compounds"][0]
        else:
            compound = data

        # Atoms
        atoms_raw = compound.get("atoms", {})
        aids = atoms_raw.get("aid", [])
        elements = atoms_raw.get("element", [])
        
        atoms = []
        for aid, el in zip(aids, elements):
            atoms.append({'element': el, 'aid': aid})
            
        # Bonds
        bonds_raw = compound.get("bonds", {})
        aid1s = bonds_raw.get("aid1", [])
        aid2s = bonds_raw.get("aid2", [])
        orders = bonds_raw.get("order", [])
        
        bonds = []
        for a1, a2, o in zip(aid1s, aid2s, orders):
            bonds.append({'aid1': a1, 'aid2': a2, 'order': o})

        # Coords
        coords = []
        coords_raw_list = compound.get("coords", [])
        if coords_raw_list:
            # Taking first conformer of first coord set
            conf_list = coords_raw_list[0].get("conformers", [])
            if conf_list:
                conf = conf_list[0]
                xs = conf.get("x", [])
                ys = conf.get("y", [])
                zs = conf.get("z", [0]*len(xs)) # Z might be missing in 2D
                
                for x, y, z in zip(xs, ys, zs):
                    coords.append([x, y, z])
        
        # Mapping aid to index
        aid_to_idx = {a['aid']: i for i, a in enumerate(atoms)}

        remapped_bonds = []
        for b in bonds:
            if b['aid1'] in aid_to_idx and b['aid2'] in aid_to_idx:
                remapped_bonds.append({
                    'aid1': aid_to_idx[b['aid1']] + 1,
                    'aid2': aid_to_idx[b['aid2']] + 1,
                    'order': b['order']
                })

        # Attach coordinates to atoms when length matches.
        if coords and len(coords) == len(atoms):
            for atom, coord in zip(atoms, coords):
                atom.setdefault('coords', coord)

        dimensionality = 3 if any(len(c) > 2 and abs(c[2]) > 1e-6 for c in coords) else 2
        
        return {
            'atoms': atoms,
            'bonds': remapped_bonds,
            'coords': coords,
            'dimensionality': dimensionality,
        }

    except Exception as e:
        print(f"Error parsing JSON data: {e}")
        return None
