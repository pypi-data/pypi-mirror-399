"""
Centralized constants and configuration for the Calculus-Core Streamlit App.
"""

# Default Example Data
EXEMPLO_SPT = [
    {'prof': 1, 'n_spt': 4, 'solo': 'Argila Siltosa'},
    {'prof': 2, 'n_spt': 5, 'solo': 'Argila Siltosa'},
    {'prof': 3, 'n_spt': 6, 'solo': 'Argila Arenosa'},
    {'prof': 4, 'n_spt': 9, 'solo': 'Argila Arenosa'},
    {'prof': 5, 'n_spt': 12, 'solo': 'Areia Argilosa'},
    {'prof': 6, 'n_spt': 18, 'solo': 'Areia Argilosa'},
    {'prof': 7, 'n_spt': 22, 'solo': 'Areia Siltosa'},
    {'prof': 8, 'n_spt': 28, 'solo': 'Areia Siltosa'},
    {'prof': 9, 'n_spt': 35, 'solo': 'Areia'},
    {'prof': 10, 'n_spt': 42, 'solo': 'Areia'},
]

# Map for user-friendly names in UI to domain identifiers
SOLOS_VALIDOS_MAP = {
    'Argila': 'argila',
    'Argila Arenosa': 'argila_arenosa',
    'Argila Areno Siltosa': 'argila_areno_siltosa',
    'Argila Siltosa': 'argila_siltosa',
    'Argila Silto Arenosa': 'argila_silto_arenosa',
    'Silte': 'silte',
    'Silte Arenoso': 'silte_arenoso',
    'Silte Areno Argiloso': 'silte_areno_argiloso',
    'Silte Argiloso': 'silte_argiloso',
    'Silte Argilo Arenoso': 'silte_argilo_arenoso',
    'Areia': 'areia',
    'Areia com Pedregulhos': 'areia_com_pedregulhos',
    'Areia Siltosa': 'areia_siltosa',
    'Areia Silto Argilosa': 'areia_silto_argilosa',
    'Areia Argilosa': 'areia_argilosa',
    'Areia Argilo Siltosa': 'areia_argilo_siltosa',
    'Solo Residual (Geral)': 'br_solo_residual_geral',
}

# Simplified map for initialization (legacy support/easy init)
SOLOS_MAP_INIT = {
    'Argila Siltosa': 'argila_siltosa',
    'Argila Arenosa': 'argila_arenosa',
    'Areia Argilosa': 'areia_argilosa',
    'Areia Siltosa': 'areia_siltosa',
    'Areia': 'areia',
}
