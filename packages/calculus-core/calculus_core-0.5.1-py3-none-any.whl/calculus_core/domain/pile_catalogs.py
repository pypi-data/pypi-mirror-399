"""
Pile Catalogs - Pre-defined Pile Configurations

This module contains catalogs of common pile configurations used in
Brazilian foundation engineering practice. Each pile type has a catalog
of standard sizes/configurations with the option for custom usage.

Catalogs include:
- Estacas Pré-Moldadas de Concreto
- Estacas Escavadas
- Estacas Hélice Contínua
- Estacas Raiz
- Estacas Franki
- Estacas Metálicas (já implementado em pile_types.py)
"""

import math
from dataclasses import dataclass
from typing import Literal

# =============================================================================
# PRE-MOLDADAS (PRECAST CONCRETE PILES)
# =============================================================================


@dataclass(frozen=True)
class PerfilPreMoldada:
    """
    Profile for precast concrete piles.

    Contains standard dimensions and structural properties.
    """

    nome: str
    formato: Literal['circular', 'quadrada', 'hexagonal', 'octogonal']
    dimensao_principal: float  # m (diameter for circular, side for square)
    area: float  # m²
    perimetro: float  # m
    peso_linear: float  # kN/m (weight per meter)
    fck: float = 35.0  # MPa (concrete characteristic strength)
    armadura: str | None = None  # Reinforcement description
    capacidade_estrutural: float | None = None  # kN (structural capacity)


# Catalog of common precast concrete piles (based on Brazilian manufacturers)
CATALOGO_PRE_MOLDADAS = {
    # Circular vibrated/centrifuged piles
    'CIRCULAR_180': PerfilPreMoldada(
        nome='Circular Ø180mm',
        formato='circular',
        dimensao_principal=0.18,
        area=math.pi * (0.09**2),
        perimetro=math.pi * 0.18,
        peso_linear=0.60,
        capacidade_estrutural=200,
    ),
    'CIRCULAR_200': PerfilPreMoldada(
        nome='Circular Ø200mm',
        formato='circular',
        dimensao_principal=0.20,
        area=math.pi * (0.10**2),
        perimetro=math.pi * 0.20,
        peso_linear=0.75,
        capacidade_estrutural=300,
    ),
    'CIRCULAR_260': PerfilPreMoldada(
        nome='Circular Ø260mm',
        formato='circular',
        dimensao_principal=0.26,
        area=math.pi * (0.13**2),
        perimetro=math.pi * 0.26,
        peso_linear=1.30,
        capacidade_estrutural=500,
    ),
    'CIRCULAR_330': PerfilPreMoldada(
        nome='Circular Ø330mm',
        formato='circular',
        dimensao_principal=0.33,
        area=math.pi * (0.165**2),
        perimetro=math.pi * 0.33,
        peso_linear=2.10,
        capacidade_estrutural=800,
    ),
    'CIRCULAR_420': PerfilPreMoldada(
        nome='Circular Ø420mm',
        formato='circular',
        dimensao_principal=0.42,
        area=math.pi * (0.21**2),
        perimetro=math.pi * 0.42,
        peso_linear=3.40,
        capacidade_estrutural=1200,
    ),
    'CIRCULAR_500': PerfilPreMoldada(
        nome='Circular Ø500mm',
        formato='circular',
        dimensao_principal=0.50,
        area=math.pi * (0.25**2),
        perimetro=math.pi * 0.50,
        peso_linear=4.80,
        capacidade_estrutural=1600,
    ),
    'CIRCULAR_600': PerfilPreMoldada(
        nome='Circular Ø600mm',
        formato='circular',
        dimensao_principal=0.60,
        area=math.pi * (0.30**2),
        perimetro=math.pi * 0.60,
        peso_linear=6.90,
        capacidade_estrutural=2200,
    ),
    # Square piles
    'QUADRADA_200': PerfilPreMoldada(
        nome='Quadrada 200x200mm',
        formato='quadrada',
        dimensao_principal=0.20,
        area=0.04,
        perimetro=0.80,
        peso_linear=1.00,
        capacidade_estrutural=350,
    ),
    'QUADRADA_250': PerfilPreMoldada(
        nome='Quadrada 250x250mm',
        formato='quadrada',
        dimensao_principal=0.25,
        area=0.0625,
        perimetro=1.00,
        peso_linear=1.55,
        capacidade_estrutural=550,
    ),
    'QUADRADA_300': PerfilPreMoldada(
        nome='Quadrada 300x300mm',
        formato='quadrada',
        dimensao_principal=0.30,
        area=0.09,
        perimetro=1.20,
        peso_linear=2.25,
        capacidade_estrutural=800,
    ),
    'QUADRADA_350': PerfilPreMoldada(
        nome='Quadrada 350x350mm',
        formato='quadrada',
        dimensao_principal=0.35,
        area=0.1225,
        perimetro=1.40,
        peso_linear=3.05,
        capacidade_estrutural=1100,
    ),
    'QUADRADA_400': PerfilPreMoldada(
        nome='Quadrada 400x400mm',
        formato='quadrada',
        dimensao_principal=0.40,
        area=0.16,
        perimetro=1.60,
        peso_linear=4.00,
        capacidade_estrutural=1400,
    ),
    'QUADRADA_450': PerfilPreMoldada(
        nome='Quadrada 450x450mm',
        formato='quadrada',
        dimensao_principal=0.45,
        area=0.2025,
        perimetro=1.80,
        peso_linear=5.05,
        capacidade_estrutural=1750,
    ),
}


# =============================================================================
# ESCAVADAS (BORED PILES)
# =============================================================================


@dataclass(frozen=True)
class PerfilEscavada:
    """
    Profile for bored piles.

    Contains standard dimensions and execution parameters.
    """

    nome: str
    diametro: float  # m
    area: float  # m²
    perimetro: float  # m
    tipo_execucao: Literal[
        'sem_revestimento', 'com_revestimento', 'com_fluido'
    ]
    profundidade_maxima: float | None = None  # m
    fck_minimo: float = 20.0  # MPa
    notas: str | None = None


# Catalog of common bored pile configurations
CATALOGO_ESCAVADAS = {
    # Small diameter without casing
    'ESCAVADA_250': PerfilEscavada(
        nome='Escavada Ø250mm',
        diametro=0.25,
        area=math.pi * (0.125**2),
        perimetro=math.pi * 0.25,
        tipo_execucao='sem_revestimento',
        profundidade_maxima=8,
    ),
    'ESCAVADA_300': PerfilEscavada(
        nome='Escavada Ø300mm',
        diametro=0.30,
        area=math.pi * (0.15**2),
        perimetro=math.pi * 0.30,
        tipo_execucao='sem_revestimento',
        profundidade_maxima=10,
    ),
    'ESCAVADA_400': PerfilEscavada(
        nome='Escavada Ø400mm',
        diametro=0.40,
        area=math.pi * (0.20**2),
        perimetro=math.pi * 0.40,
        tipo_execucao='sem_revestimento',
        profundidade_maxima=12,
    ),
    # With casing
    'ESCAVADA_500_REV': PerfilEscavada(
        nome='Escavada Ø500mm c/ Revestimento',
        diametro=0.50,
        area=math.pi * (0.25**2),
        perimetro=math.pi * 0.50,
        tipo_execucao='com_revestimento',
        profundidade_maxima=25,
    ),
    'ESCAVADA_600_REV': PerfilEscavada(
        nome='Escavada Ø600mm c/ Revestimento',
        diametro=0.60,
        area=math.pi * (0.30**2),
        perimetro=math.pi * 0.60,
        tipo_execucao='com_revestimento',
        profundidade_maxima=30,
    ),
    'ESCAVADA_800_REV': PerfilEscavada(
        nome='Escavada Ø800mm c/ Revestimento',
        diametro=0.80,
        area=math.pi * (0.40**2),
        perimetro=math.pi * 0.80,
        tipo_execucao='com_revestimento',
        profundidade_maxima=35,
    ),
    'ESCAVADA_1000_REV': PerfilEscavada(
        nome='Escavada Ø1000mm c/ Revestimento',
        diametro=1.00,
        area=math.pi * (0.50**2),
        perimetro=math.pi * 1.00,
        tipo_execucao='com_revestimento',
        profundidade_maxima=40,
    ),
    # With bentonite fluid
    'ESCAVADA_800_FLUIDO': PerfilEscavada(
        nome='Escavada Ø800mm c/ Fluido',
        diametro=0.80,
        area=math.pi * (0.40**2),
        perimetro=math.pi * 0.80,
        tipo_execucao='com_fluido',
        profundidade_maxima=50,
        notas='Estabilização com lama bentonítica ou polímero',
    ),
    'ESCAVADA_1200_FLUIDO': PerfilEscavada(
        nome='Escavada Ø1200mm c/ Fluido',
        diametro=1.20,
        area=math.pi * (0.60**2),
        perimetro=math.pi * 1.20,
        tipo_execucao='com_fluido',
        profundidade_maxima=60,
        notas='Estabilização com lama bentonítica ou polímero',
    ),
    'ESCAVADA_1500_FLUIDO': PerfilEscavada(
        nome='Escavada Ø1500mm c/ Fluido',
        diametro=1.50,
        area=math.pi * (0.75**2),
        perimetro=math.pi * 1.50,
        tipo_execucao='com_fluido',
        profundidade_maxima=70,
        notas='Estabilização com lama bentonítica ou polímero',
    ),
}


# =============================================================================
# HÉLICE CONTÍNUA (CONTINUOUS FLIGHT AUGER - CFA)
# =============================================================================


@dataclass(frozen=True)
class PerfilHeliceContinua:
    """
    Profile for CFA (Continuous Flight Auger) piles.

    Contains standard dimensions and equipment specifications.
    """

    nome: str
    diametro: float  # m
    area: float  # m²
    perimetro: float  # m
    profundidade_maxima: float  # m
    torque_minimo: float  # kNm (minimum equipment torque)
    fck_minimo: float = 20.0  # MPa
    slump_concreto: str = '22 ± 3 cm'


# Catalog of common CFA pile configurations
CATALOGO_HELICE_CONTINUA = {
    'HELICE_300': PerfilHeliceContinua(
        nome='Hélice Contínua Ø300mm',
        diametro=0.30,
        area=math.pi * (0.15**2),
        perimetro=math.pi * 0.30,
        profundidade_maxima=15,
        torque_minimo=50,
    ),
    'HELICE_350': PerfilHeliceContinua(
        nome='Hélice Contínua Ø350mm',
        diametro=0.35,
        area=math.pi * (0.175**2),
        perimetro=math.pi * 0.35,
        profundidade_maxima=18,
        torque_minimo=70,
    ),
    'HELICE_400': PerfilHeliceContinua(
        nome='Hélice Contínua Ø400mm',
        diametro=0.40,
        area=math.pi * (0.20**2),
        perimetro=math.pi * 0.40,
        profundidade_maxima=21,
        torque_minimo=90,
    ),
    'HELICE_500': PerfilHeliceContinua(
        nome='Hélice Contínua Ø500mm',
        diametro=0.50,
        area=math.pi * (0.25**2),
        perimetro=math.pi * 0.50,
        profundidade_maxima=24,
        torque_minimo=130,
    ),
    'HELICE_600': PerfilHeliceContinua(
        nome='Hélice Contínua Ø600mm',
        diametro=0.60,
        area=math.pi * (0.30**2),
        perimetro=math.pi * 0.60,
        profundidade_maxima=27,
        torque_minimo=180,
    ),
    'HELICE_700': PerfilHeliceContinua(
        nome='Hélice Contínua Ø700mm',
        diametro=0.70,
        area=math.pi * (0.35**2),
        perimetro=math.pi * 0.70,
        profundidade_maxima=28,
        torque_minimo=230,
    ),
    'HELICE_800': PerfilHeliceContinua(
        nome='Hélice Contínua Ø800mm',
        diametro=0.80,
        area=math.pi * (0.40**2),
        perimetro=math.pi * 0.80,
        profundidade_maxima=30,
        torque_minimo=300,
    ),
    'HELICE_1000': PerfilHeliceContinua(
        nome='Hélice Contínua Ø1000mm',
        diametro=1.00,
        area=math.pi * (0.50**2),
        perimetro=math.pi * 1.00,
        profundidade_maxima=32,
        torque_minimo=450,
    ),
    'HELICE_1200': PerfilHeliceContinua(
        nome='Hélice Contínua Ø1200mm',
        diametro=1.20,
        area=math.pi * (0.60**2),
        perimetro=math.pi * 1.20,
        profundidade_maxima=32,
        torque_minimo=600,
    ),
}


# =============================================================================
# RAIZ (MICROPILES / ROOT PILES)
# =============================================================================


@dataclass(frozen=True)
class PerfilRaiz:
    """
    Profile for root piles (micropiles).

    Contains standard dimensions and injection parameters.
    """

    nome: str
    diametro_perfuracao: float  # m
    diametro_efetivo: float  # m (after injection)
    area: float  # m²
    perimetro: float  # m
    tipo_injecao: Literal['unica', 'multipla']
    pressao_injecao: float | None = None  # MPa
    profundidade_maxima: float | None = None  # m
    inclinacao_maxima: float = 45.0  # degrees


# Catalog of common root pile configurations
CATALOGO_RAIZ = {
    'RAIZ_100': PerfilRaiz(
        nome='Raiz Ø100mm',
        diametro_perfuracao=0.10,
        diametro_efetivo=0.12,
        area=math.pi * (0.06**2),
        perimetro=math.pi * 0.12,
        tipo_injecao='unica',
        profundidade_maxima=20,
    ),
    'RAIZ_120': PerfilRaiz(
        nome='Raiz Ø120mm',
        diametro_perfuracao=0.12,
        diametro_efetivo=0.15,
        area=math.pi * (0.075**2),
        perimetro=math.pi * 0.15,
        tipo_injecao='unica',
        profundidade_maxima=22,
    ),
    'RAIZ_160': PerfilRaiz(
        nome='Raiz Ø160mm',
        diametro_perfuracao=0.16,
        diametro_efetivo=0.20,
        area=math.pi * (0.10**2),
        perimetro=math.pi * 0.20,
        tipo_injecao='unica',
        profundidade_maxima=25,
    ),
    'RAIZ_200': PerfilRaiz(
        nome='Raiz Ø200mm',
        diametro_perfuracao=0.20,
        diametro_efetivo=0.25,
        area=math.pi * (0.125**2),
        perimetro=math.pi * 0.25,
        tipo_injecao='unica',
        profundidade_maxima=28,
    ),
    'RAIZ_250': PerfilRaiz(
        nome='Raiz Ø250mm',
        diametro_perfuracao=0.25,
        diametro_efetivo=0.30,
        area=math.pi * (0.15**2),
        perimetro=math.pi * 0.30,
        tipo_injecao='unica',
        profundidade_maxima=30,
    ),
    'RAIZ_310': PerfilRaiz(
        nome='Raiz Ø310mm',
        diametro_perfuracao=0.31,
        diametro_efetivo=0.35,
        area=math.pi * (0.175**2),
        perimetro=math.pi * 0.35,
        tipo_injecao='multipla',
        pressao_injecao=2.0,
        profundidade_maxima=35,
    ),
    'RAIZ_410': PerfilRaiz(
        nome='Raiz Ø410mm',
        diametro_perfuracao=0.41,
        diametro_efetivo=0.45,
        area=math.pi * (0.225**2),
        perimetro=math.pi * 0.45,
        tipo_injecao='multipla',
        pressao_injecao=3.0,
        profundidade_maxima=40,
    ),
}


# =============================================================================
# FRANKI (DRIVEN CAST-IN-PLACE)
# =============================================================================


@dataclass(frozen=True)
class PerfilFranki:
    """
    Profile for Franki piles (driven cast-in-place with expanded base).

    Contains standard dimensions and base expansion parameters.
    """

    nome: str
    diametro_tubo: float  # m
    diametro_fuste: float  # m
    diametro_base: float  # m (expanded base)
    area_fuste: float  # m²
    area_base: float  # m²
    perimetro_fuste: float  # m
    energia_cravacao: float  # kJ (typical driving energy)
    capacidade_tipica: float | None = None  # kN


# Catalog of common Franki pile configurations
CATALOGO_FRANKI = {
    'FRANKI_350': PerfilFranki(
        nome='Franki Ø350mm',
        diametro_tubo=0.35,
        diametro_fuste=0.35,
        diametro_base=0.55,
        area_fuste=math.pi * (0.175**2),
        area_base=math.pi * (0.275**2),
        perimetro_fuste=math.pi * 0.35,
        energia_cravacao=30,
        capacidade_tipica=600,
    ),
    'FRANKI_400': PerfilFranki(
        nome='Franki Ø400mm',
        diametro_tubo=0.40,
        diametro_fuste=0.40,
        diametro_base=0.65,
        area_fuste=math.pi * (0.20**2),
        area_base=math.pi * (0.325**2),
        perimetro_fuste=math.pi * 0.40,
        energia_cravacao=40,
        capacidade_tipica=900,
    ),
    'FRANKI_450': PerfilFranki(
        nome='Franki Ø450mm',
        diametro_tubo=0.45,
        diametro_fuste=0.45,
        diametro_base=0.70,
        area_fuste=math.pi * (0.225**2),
        area_base=math.pi * (0.35**2),
        perimetro_fuste=math.pi * 0.45,
        energia_cravacao=50,
        capacidade_tipica=1200,
    ),
    'FRANKI_520': PerfilFranki(
        nome='Franki Ø520mm',
        diametro_tubo=0.52,
        diametro_fuste=0.52,
        diametro_base=0.80,
        area_fuste=math.pi * (0.26**2),
        area_base=math.pi * (0.40**2),
        perimetro_fuste=math.pi * 0.52,
        energia_cravacao=60,
        capacidade_tipica=1500,
    ),
    'FRANKI_600': PerfilFranki(
        nome='Franki Ø600mm',
        diametro_tubo=0.60,
        diametro_fuste=0.60,
        diametro_base=0.90,
        area_fuste=math.pi * (0.30**2),
        area_base=math.pi * (0.45**2),
        perimetro_fuste=math.pi * 0.60,
        energia_cravacao=75,
        capacidade_tipica=2000,
    ),
}


# =============================================================================
# ÔMEGA (OMEGA PILES)
# =============================================================================


@dataclass(frozen=True)
class PerfilOmega:
    """
    Profile for Omega piles (displacement screw pile).

    Similar to CFA but with soil displacement instead of removal.
    """

    nome: str
    diametro: float  # m
    area: float  # m²
    perimetro: float  # m
    profundidade_maxima: float  # m
    torque_minimo: float  # kNm


# Catalog of common Omega pile configurations
CATALOGO_OMEGA = {
    'OMEGA_310': PerfilOmega(
        nome='Ômega Ø310mm',
        diametro=0.31,
        area=math.pi * (0.155**2),
        perimetro=math.pi * 0.31,
        profundidade_maxima=18,
        torque_minimo=60,
    ),
    'OMEGA_360': PerfilOmega(
        nome='Ômega Ø360mm',
        diametro=0.36,
        area=math.pi * (0.18**2),
        perimetro=math.pi * 0.36,
        profundidade_maxima=20,
        torque_minimo=80,
    ),
    'OMEGA_410': PerfilOmega(
        nome='Ômega Ø410mm',
        diametro=0.41,
        area=math.pi * (0.205**2),
        perimetro=math.pi * 0.41,
        profundidade_maxima=22,
        torque_minimo=100,
    ),
    'OMEGA_460': PerfilOmega(
        nome='Ômega Ø460mm',
        diametro=0.46,
        area=math.pi * (0.23**2),
        perimetro=math.pi * 0.46,
        profundidade_maxima=24,
        torque_minimo=130,
    ),
    'OMEGA_510': PerfilOmega(
        nome='Ômega Ø510mm',
        diametro=0.51,
        area=math.pi * (0.255**2),
        perimetro=math.pi * 0.51,
        profundidade_maxima=26,
        torque_minimo=170,
    ),
    'OMEGA_610': PerfilOmega(
        nome='Ômega Ø610mm',
        diametro=0.61,
        area=math.pi * (0.305**2),
        perimetro=math.pi * 0.61,
        profundidade_maxima=28,
        torque_minimo=230,
    ),
}


# =============================================================================
# UNIFIED CATALOG ACCESS
# =============================================================================


# Type alias for any profile type
PerfilType = (
    PerfilPreMoldada
    | PerfilEscavada
    | PerfilHeliceContinua
    | PerfilRaiz
    | PerfilFranki
    | PerfilOmega
)


# Unified catalog registry
CATALOGOS = {
    'pre_moldada': CATALOGO_PRE_MOLDADAS,
    'escavada': CATALOGO_ESCAVADAS,
    'helice_continua': CATALOGO_HELICE_CONTINUA,
    'raiz': CATALOGO_RAIZ,
    'franki': CATALOGO_FRANKI,
    'omega': CATALOGO_OMEGA,
}


def listar_tipos_estaca() -> list[str]:
    """List all available pile types with catalogs."""
    return list(CATALOGOS.keys())


def listar_perfis_por_tipo(tipo_estaca: str) -> list[str]:
    """
    List all available profiles for a pile type.

    Args:
        tipo_estaca: Pile type name.

    Returns:
        List of profile names.
    """
    tipo_norm = tipo_estaca.lower().replace(' ', '_').replace('-', '_')

    # Handle aliases
    aliases = {
        'premoldada': 'pre_moldada',
        'pré_moldada': 'pre_moldada',
        'hélice': 'helice_continua',
        'cfa': 'helice_continua',
        'micropile': 'raiz',
        'microestaca': 'raiz',
        'ômega': 'omega',
    }

    if tipo_norm in aliases:
        tipo_norm = aliases[tipo_norm]

    if tipo_norm not in CATALOGOS:
        available = ', '.join(CATALOGOS.keys())
        raise ValueError(
            f'Tipo de estaca "{tipo_estaca}" não encontrado. '
            f'Disponíveis: {available}'
        )

    return list(CATALOGOS[tipo_norm].keys())


def obter_perfil(tipo_estaca: str, nome_perfil: str) -> PerfilType:
    """
    Get a specific profile from a catalog.

    Args:
        tipo_estaca: Pile type name.
        nome_perfil: Profile name.

    Returns:
        The profile object.
    """
    tipo_norm = tipo_estaca.lower().replace(' ', '_').replace('-', '_')

    # Handle aliases
    aliases = {
        'premoldada': 'pre_moldada',
        'pré_moldada': 'pre_moldada',
        'hélice': 'helice_continua',
        'cfa': 'helice_continua',
        'micropile': 'raiz',
        'microestaca': 'raiz',
        'ômega': 'omega',
    }

    if tipo_norm in aliases:
        tipo_norm = aliases[tipo_norm]

    if tipo_norm not in CATALOGOS:
        raise ValueError(f'Tipo de estaca "{tipo_estaca}" não encontrado.')

    catalogo = CATALOGOS[tipo_norm]

    if nome_perfil not in catalogo:
        available = ', '.join(catalogo.keys())
        raise ValueError(
            f'Perfil "{nome_perfil}" não encontrado em {tipo_estaca}. '
            f'Disponíveis: {available}'
        )

    return catalogo[nome_perfil]


def buscar_perfil_por_diametro(
    tipo_estaca: str,
    diametro: float,
    tolerancia: float = 0.02,
) -> PerfilType | None:
    """
    Find a profile by approximate diameter.

    Args:
        tipo_estaca: Pile type name.
        diametro: Target diameter in meters.
        tolerancia: Tolerance for matching (default 2cm).

    Returns:
        Matching profile or None.
    """
    perfis = listar_perfis_por_tipo(tipo_estaca)
    catalogo = CATALOGOS[tipo_estaca.lower()]

    for nome in perfis:
        perfil = catalogo[nome]
        # Get diameter based on profile type
        if hasattr(perfil, 'diametro'):
            d = perfil.diametro
        elif hasattr(perfil, 'dimensao_principal'):
            d = perfil.dimensao_principal
        elif hasattr(perfil, 'diametro_fuste'):
            d = perfil.diametro_fuste
        else:
            continue

        if abs(d - diametro) <= tolerancia:
            return perfil

    return None


def resumo_catalogos() -> dict[str, list[dict]]:
    """
    Get a summary of all catalogs.

    Returns:
        Dictionary with pile types and their profiles info.
    """
    resumo = {}

    for tipo, catalogo in CATALOGOS.items():
        perfis_info = []
        for nome, perfil in catalogo.items():
            info = {'nome': nome, 'descricao': perfil.nome}

            # Add diameter info
            if hasattr(perfil, 'diametro'):
                info['diametro_m'] = perfil.diametro
            elif hasattr(perfil, 'dimensao_principal'):
                info['diametro_m'] = perfil.dimensao_principal
            elif hasattr(perfil, 'diametro_fuste'):
                info['diametro_m'] = perfil.diametro_fuste

            # Add area and perimeter
            if hasattr(perfil, 'area'):
                info['area_m2'] = perfil.area
            if hasattr(perfil, 'area_base'):
                info['area_base_m2'] = perfil.area_base
            if hasattr(perfil, 'perimetro'):
                info['perimetro_m'] = perfil.perimetro

            perfis_info.append(info)

        resumo[tipo] = perfis_info

    return resumo
