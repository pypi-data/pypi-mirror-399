# Chemanim

[![PyPI version](https://badge.fury.io/py/chemanim.svg)](https://pypi.org/project/chemanim/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library extended from [ManimGL](https://github.com/3b1b/manim) for creating chemistry and biochemistry animations.

## Features

- **Core Chemistry**: Visualize Atoms, Bonds, and Molecules.
- **Trusted Data**: Fetch molecular structures directly from PubChem.
- **Biochemistry**: Parse and visualize PDB structures (Proteins/DNA).
- **3D Molecules**: Render ball-and-stick, space-filling, and wireframe structures.
- **Protein Visualization**: Cartoon ribbon diagrams with secondary structure coloring.
- **Reactions**: Animate chemical reactions simply.

## Installation

Install from PyPI:

```bash
pip install chemanim
```

### Interactive Setup (Recommended)

After installation, run the setup wizard to install optional features:

```bash
chemanim-setup
```

This will show an interactive menu to choose what you need:
- **All Features** ⭐ - ManimGL + RDKit + ChemPy + Biotite + py3Dmol
- **Animations Only** - Just ManimGL
- **Chemistry Analysis** - RDKit + ChemPy + ChemFormula
- **Protein Analysis** - Just Biotite
- **3D Viewer** - Just py3Dmol

### Manual Installation

Or install optional dependencies directly:

| Command | What it adds |
|---------|--------------|
| `pip install chemanim[vis]` | ManimGL for animations |
| `pip install chemanim[chem]` | RDKit + ChemPy + ChemFormula for molecular analysis |
| `pip install chemanim[bio]` | Biotite for protein secondary structure analysis |
| `pip install chemanim[viewer]` | py3Dmol for interactive 3D viewing |
| `pip install chemanim[all]` | All optional dependencies |

### Core Dependencies (installed automatically)

- `numpy` - Numerical operations
- `requests` - HTTP requests for PubChem
- `pubchempy` - PubChem API wrapper
- `biopython` - PDB file parsing
- `networkx` - Molecular graph operations

### Development Installation

For local development:

```bash
git clone https://github.com/Wachirawut2023/Chemanim.git
cd Chemanim
pip install -e .[all]
```

## Usage

See `examples/` folder for demo scripts.

### Basic Animation

```bash
manimgl examples/demo_reaction.py SimpleReactionScene
```

### 3D Molecule Visualization

```bash
manimgl examples/demo_3d_molecule.py Molecule3DDemo
```

### Protein Visualization

```bash
manimgl examples/demo_protein_styles.py ProteinStylesDemo
```

### Interactive 3D Viewer (py3Dmol)

```python
from chemanim.connect import fetch_molecule_data
from chemanim.viewer_3d import show_py3dmol, write_xyz

data = fetch_molecule_data("benzene")
view = show_py3dmol(data, style="ball_and_stick")
view.write_html("benzene.html")
write_xyz("benzene.xyz", data)
```

## Examples

| Example | Description |
|---------|-------------|
| `demo_pubchem.py` | Fetch and display molecules from PubChem |
| `demo_reaction.py` | Simple chemical reaction animation |
| `demo_render_styles.py` | Ball-and-stick, space-filling, wireframe |
| `demo_protein_styles.py` | Protein cartoon, backbone, and atom views |
| `demo_py3dmol_viewer.py` | Interactive HTML 3D viewer |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Wachirawut Raksawat ([@Wachirawut2023](https://github.com/Wachirawut2023))
