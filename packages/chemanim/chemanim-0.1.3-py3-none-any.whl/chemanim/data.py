# Periodic Table Data
# Colors are hex codes

PERIODIC_TABLE = {
    1: {"symbol": "H", "name": "Hydrogen", "color": "#FFFFFF", "mass": 1.008, "radius": 0.53},
    2: {"symbol": "He", "name": "Helium", "color": "#D9FFFF", "mass": 4.0026, "radius": 0.31},
    3: {"symbol": "Li", "name": "Lithium", "color": "#CC80FF", "mass": 6.94, "radius": 1.67},
    4: {"symbol": "Be", "name": "Beryllium", "color": "#C2FF00", "mass": 9.0122, "radius": 1.12},
    5: {"symbol": "B", "name": "Boron", "color": "#FFB5B5", "mass": 10.81, "radius": 0.87},
    6: {"symbol": "C", "name": "Carbon", "color": "#909090", "mass": 12.011, "radius": 0.67},
    7: {"symbol": "N", "name": "Nitrogen", "color": "#3050F8", "mass": 14.007, "radius": 0.56},
    8: {"symbol": "O", "name": "Oxygen", "color": "#FF0D0D", "mass": 15.999, "radius": 0.48},
    9: {"symbol": "F", "name": "Fluorine", "color": "#90E050", "mass": 18.998, "radius": 0.42},
    10: {"symbol": "Ne", "name": "Neon", "color": "#B3E3F5", "mass": 20.180, "radius": 0.38},
    11: {"symbol": "Na", "name": "Sodium", "color": "#AB5CF2", "mass": 22.990, "radius": 1.90},
    12: {"symbol": "Mg", "name": "Magnesium", "color": "#8AFF00", "mass": 24.305, "radius": 1.45},
    13: {"symbol": "Al", "name": "Aluminium", "color": "#BFA6A6", "mass": 26.982, "radius": 1.18},
    14: {"symbol": "Si", "name": "Silicon", "color": "#F0C8A0", "mass": 28.085, "radius": 1.11},
    15: {"symbol": "P", "name": "Phosphorus", "color": "#FF8000", "mass": 30.974, "radius": 0.98},
    16: {"symbol": "S", "name": "Sulfur", "color": "#FFFF30", "mass": 32.06, "radius": 0.88},
    17: {"symbol": "Cl", "name": "Chlorine", "color": "#1FF01F", "mass": 35.45, "radius": 0.79},
    18: {"symbol": "Ar", "name": "Argon", "color": "#80D1E3", "mass": 39.948, "radius": 0.71},
    # Add more as needed...
}

def get_element_data(identifier):
    """
    Get element data by atomic number (int) or symbol (str).
    """
    if isinstance(identifier, int):
        return PERIODIC_TABLE.get(identifier)
    elif isinstance(identifier, str):
        for data in PERIODIC_TABLE.values():
            if data["symbol"] == identifier:
                return data
    return None
