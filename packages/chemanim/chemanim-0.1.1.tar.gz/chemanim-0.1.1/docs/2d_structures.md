# 2D Structure Features in Chemanim

This document summarizes how to build and animate 2D chemical structures with Chemanim. It covers coordinate sources, depiction modes, functional-group overlays, reactions, and per-atom/bond control APIs.

## Quick start

Install optional deps if you want RDKit-driven layouts and ChemPy parsing:

```
pip install rdkit-pypi chempy
```

Render a simple scene (skeletal ethanol with functional-group overlay):

```python
from manim import *
from chemanim.chem_object import ChemObject
from chemanim.rdkit_adapter import detect_functional_groups, functional_group_palette, molecule_data_from_smiles

class Example(Scene):
    def construct(self):
        data = molecule_data_from_smiles("CCO")
        fg = detect_functional_groups("CCO")
        mol = ChemObject(
            data,
            skeletal=True,
            use_external_coords=True,
            skeletal_carbon_marker_radius=0.06,
            skeletal_carbon_marker_color=GREY_C,
        )
        mol.add_functional_group_highlights(fg, palette=functional_group_palette())
        self.add(mol)
        self.wait(1)
```

Run: `python -m manim -pql your_scene.py Example`

## Coordinate sources

- RDKit (default when SMILES present): `ChemObject` will call `compute_rdkit_2d_coords` if coordinates are missing and `use_external_coords=True`.
- External JSON/PubChem: pass parsed molecule data with `atoms/bonds/coords` and optional `smiles`.
- Internal layout fallback: if no coordinates are available or RDKit is absent, coordinates are generated procedurally.

## Depiction modes

- `skeletal=True`: omits hydrogens, hides carbon labels, optional carbon markers via `skeletal_carbon_marker_radius/color`.
- `straight_chain=True`: linear backbone layout.
- `zigzag_chain=True`: classical zigzag backbone.
- Default (VSEPR-inspired) layout when no chain flags are set.

Common knobs: `bond_length`, `bond_stroke`, `font_size`, `use_external_coords`.

## Functional groups

- Detection via RDKit SMARTS: `detect_functional_groups(smiles, add_h=False)` returns labeled matches keyed by category (hydrocarbon, halogen, oxygen, nitrogen, sulfur, phosphorus).
- Palette helper: `functional_group_palette()` maps categories to colors.
- Highlight overlays: `ChemObject.add_functional_group_highlights(matches, palette=..., show_labels=True, fill_opacity=0.1, stroke_width=3, buff=0.6)` draws rounded boxes and optional labels over matched atoms.

## Reactions and mechanisms

- Basic rearrangements with `ChemicalReaction` (ball-and-stick or line structures): see `examples/demo_reaction.py`, `demo_reaction_line.py`, `demo_multiple_reactions.py`.
- ChemPy parsing to ChemObjects: `chempy_adapter.build_reaction_chemobjects(equation, species_to_smiles, chemobject_kwargs={...})` (example in `examples/demo_chempy_reaction.py`).
- Mechanistic multi-step demo with FG overlays and curved arrows: `examples/demo_reaction_mechanism.py`.

## Per-atom and per-bond control

`ChemObject` exposes helpers for custom animations:

- Accessors: `get_atom(idx)`, `get_bond(aid1, aid2)`, `iter_atoms()`, `iter_bonds()`.
- Metadata: each bond stores `aid1`, `aid2`, and `order`.
- Move an atom: `self.play(mol.animate_atom_to(0, LEFT*2))`.
- Keep bonds in sync while moving atoms: call `mol.enable_dynamic_bonds()` once; bonds will update positions during animations (supports single/double/triple, skeletal or standard).

## Demos to try

- Mode comparison: `python -m manim -pql examples/demo_mode_comparison.py ModeComparison`
- Skeletal gallery: `python -m manim -pql examples/demo_skeletal_gallery.py SkeletalGallery`
- Functional groups: `python -m manim -pql examples/demo_functional_groups.py FunctionalGroupsDemo`
- Mechanistic multi-step: `python -m manim -pql examples/demo_reaction_mechanism.py MultiStepOxidation`

## Tips

- If RDKit is missing, functional-group detection and RDKit-based layouts will raise; install RDKit or set `use_external_coords=False` to rely on internal layouts.
- For clearer skeletal renders, set `bond_stroke` a bit higher (e.g., 4–5) and `skeletal_carbon_marker_radius` to a small value (e.g., 0.05–0.08) when you need visible carbon dots.
- Use `fill_opacity` on functional-group overlays sparingly to avoid obscuring bonds; 0.08–0.15 works well.
