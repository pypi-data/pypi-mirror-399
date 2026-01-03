"""
Pile Types - Specific Pile Implementations

This module contains specific pile type implementations that handle
the particularities of different pile types (steel profiles, precast, etc.)

Design Pattern: Factory + Type-specific implementations
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Literal

# =============================================================================
# BASE PILE ABSTRACTION
# =============================================================================


class EstacaBase(ABC):
    """
    Abstract base class for all pile types.

    Each concrete pile type must implement the geometric properties
    (area, perimeter) according to its specific characteristics.
    """

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Pile type identifier for coefficient lookup."""
        pass

    @property
    @abstractmethod
    def processo_construcao(self) -> str:
        """Construction process (displacement, excavated, etc.)."""
        pass

    @property
    @abstractmethod
    def area_ponta(self) -> float:
        """Tip area in m²."""
        pass

    @property
    @abstractmethod
    def perimetro(self) -> float:
        """Perimeter in m."""
        pass

    @property
    @abstractmethod
    def cota_assentamento(self) -> int:
        """Installation depth."""
        pass

    @property
    @abstractmethod
    def secao_transversal(self) -> float:
        """Cross-section dimension (for compatibility)."""
        pass

    @abstractmethod
    def na_cota(self, nova_cota: int) -> 'EstacaBase':
        """Return a copy of the pile at a new depth."""
        pass


# =============================================================================
# CONCRETE PILE TYPES
# =============================================================================


@dataclass
class EstacaCircular(EstacaBase):
    """Circular pile (precast, bored, CFA, etc.)."""

    _tipo: str
    _processo_construcao: str
    diametro: float  # meters
    _cota_assentamento: int

    def __post_init__(self):
        if self.diametro <= 0:
            raise ValueError('Diâmetro deve ser positivo.')
        if self._cota_assentamento < 1:
            raise ValueError('Cota de assentamento deve ser >= 1.')

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def processo_construcao(self) -> str:
        return self._processo_construcao

    @property
    def cota_assentamento(self) -> int:
        return self._cota_assentamento

    @property
    def area_ponta(self) -> float:
        raio = self.diametro / 2
        return math.pi * (raio**2)

    @property
    def perimetro(self) -> float:
        return math.pi * self.diametro

    @property
    def secao_transversal(self) -> float:
        return self.diametro

    @property
    def formato(self) -> Literal['circular', 'quadrada']:
        return 'circular'

    def na_cota(self, nova_cota: int) -> 'EstacaCircular':
        return replace(self, _cota_assentamento=nova_cota)


@dataclass
class EstacaQuadrada(EstacaBase):
    """Square pile (typically precast)."""

    _tipo: str
    _processo_construcao: str
    lado: float  # meters
    _cota_assentamento: int

    def __post_init__(self):
        if self.lado <= 0:
            raise ValueError('Lado deve ser positivo.')
        if self._cota_assentamento < 1:
            raise ValueError('Cota de assentamento deve ser >= 1.')

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def processo_construcao(self) -> str:
        return self._processo_construcao

    @property
    def cota_assentamento(self) -> int:
        return self._cota_assentamento

    @property
    def area_ponta(self) -> float:
        return self.lado**2

    @property
    def perimetro(self) -> float:
        return 4 * self.lado

    @property
    def secao_transversal(self) -> float:
        return self.lado

    @property
    def formato(self) -> Literal['circular', 'quadrada']:
        return 'quadrada'

    def na_cota(self, nova_cota: int) -> 'EstacaQuadrada':
        return replace(self, _cota_assentamento=nova_cota)


# =============================================================================
# STEEL PILE PROFILES
# =============================================================================


@dataclass(frozen=True)
class PerfilMetalico:
    """
    Value object representing a steel profile specification.

    Contains all geometric and structural properties needed for
    pile calculations with steel sections.
    """

    nome: str  # e.g., "HP 310x79", "W 360x122", "Tubular 406x12.7"
    tipo_perfil: Literal['HP', 'W', 'I', 'tubular', 'caixao']
    area_secao: float  # cm² -> converted to m²
    perimetro: float  # cm -> converted to m
    # Additional properties for structural analysis
    altura: float | None = None  # mm
    largura: float | None = None  # mm
    espessura_alma: float | None = None  # mm
    espessura_mesa: float | None = None  # mm
    # For tubular sections
    diametro_externo: float | None = None  # mm
    espessura_parede: float | None = None  # mm
    # Structural properties
    momento_inercia_x: float | None = None  # cm⁴
    momento_inercia_y: float | None = None  # cm⁴
    modulo_resistencia_x: float | None = None  # cm³
    modulo_resistencia_y: float | None = None  # cm³

    @property
    def area_m2(self) -> float:
        """Area in m²."""
        return self.area_secao / 10000  # cm² to m²

    @property
    def perimetro_m(self) -> float:
        """Perimeter in m."""
        return self.perimetro / 100  # cm to m


# Catalog of common steel profiles used in Brazilian pile foundation
CATALOGO_PERFIS_METALICOS = {
    # HP Profiles (Heavy Pile)
    'HP_250x62': PerfilMetalico(
        nome='HP 250x62',
        tipo_perfil='HP',
        area_secao=79.0,
        perimetro=104.0,  # Approximate
        altura=246,
        largura=256,
        espessura_alma=10.5,
        espessura_mesa=10.7,
    ),
    'HP_310x79': PerfilMetalico(
        nome='HP 310x79',
        tipo_perfil='HP',
        area_secao=101.0,
        perimetro=126.0,
        altura=299,
        largura=306,
        espessura_alma=11.0,
        espessura_mesa=11.0,
    ),
    'HP_310x93': PerfilMetalico(
        nome='HP 310x93',
        tipo_perfil='HP',
        area_secao=119.0,
        perimetro=128.0,
        altura=303,
        largura=308,
        espessura_alma=13.1,
        espessura_mesa=13.1,
    ),
    'HP_310x110': PerfilMetalico(
        nome='HP 310x110',
        tipo_perfil='HP',
        area_secao=140.0,
        perimetro=130.0,
        altura=308,
        largura=310,
        espessura_alma=15.4,
        espessura_mesa=15.5,
    ),
    'HP_360x108': PerfilMetalico(
        nome='HP 360x108',
        tipo_perfil='HP',
        area_secao=138.0,
        perimetro=148.0,
        altura=346,
        largura=371,
        espessura_alma=12.8,
        espessura_mesa=12.8,
    ),
    'HP_360x132': PerfilMetalico(
        nome='HP 360x132',
        tipo_perfil='HP',
        area_secao=168.0,
        perimetro=152.0,
        altura=351,
        largura=373,
        espessura_alma=15.6,
        espessura_mesa=15.6,
    ),
    # W Profiles (Wide Flange)
    'W_250x73': PerfilMetalico(
        nome='W 250x73',
        tipo_perfil='W',
        area_secao=92.9,
        perimetro=110.0,
        altura=253,
        largura=254,
        espessura_alma=8.6,
        espessura_mesa=14.2,
    ),
    'W_310x97': PerfilMetalico(
        nome='W 310x97',
        tipo_perfil='W',
        area_secao=123.0,
        perimetro=130.0,
        altura=308,
        largura=305,
        espessura_alma=9.9,
        espessura_mesa=15.4,
    ),
    'W_360x122': PerfilMetalico(
        nome='W 360x122',
        tipo_perfil='W',
        area_secao=155.0,
        perimetro=150.0,
        altura=363,
        largura=257,
        espessura_alma=13.0,
        espessura_mesa=21.7,
    ),
    # Tubular profiles
    'TUBULAR_273x6.3': PerfilMetalico(
        nome='Tubular 273x6.3',
        tipo_perfil='tubular',
        area_secao=52.8,
        perimetro=85.8,
        diametro_externo=273.0,
        espessura_parede=6.3,
    ),
    'TUBULAR_323.9x7.1': PerfilMetalico(
        nome='Tubular 323.9x7.1',
        tipo_perfil='tubular',
        area_secao=70.7,
        perimetro=101.7,
        diametro_externo=323.9,
        espessura_parede=7.1,
    ),
    'TUBULAR_355.6x7.9': PerfilMetalico(
        nome='Tubular 355.6x7.9',
        tipo_perfil='tubular',
        area_secao=86.4,
        perimetro=111.7,
        diametro_externo=355.6,
        espessura_parede=7.9,
    ),
    'TUBULAR_406.4x9.5': PerfilMetalico(
        nome='Tubular 406.4x9.5',
        tipo_perfil='tubular',
        area_secao=118.5,
        perimetro=127.7,
        diametro_externo=406.4,
        espessura_parede=9.5,
    ),
    'TUBULAR_508x11': PerfilMetalico(
        nome='Tubular 508x11',
        tipo_perfil='tubular',
        area_secao=172.0,
        perimetro=159.6,
        diametro_externo=508.0,
        espessura_parede=11.0,
    ),
    'TUBULAR_610x12.7': PerfilMetalico(
        nome='Tubular 610x12.7',
        tipo_perfil='tubular',
        area_secao=238.0,
        perimetro=191.6,
        diametro_externo=610.0,
        espessura_parede=12.7,
    ),
}


@dataclass
class EstacaMetalica(EstacaBase):
    """
    Steel pile with specific profile.

    Uses pre-defined steel profiles with exact geometric properties.
    """

    perfil: PerfilMetalico
    _cota_assentamento: int
    ponta_fechada: bool = True  # Closed or open-ended

    def __post_init__(self):
        if self._cota_assentamento < 1:
            raise ValueError('Cota de assentamento deve ser >= 1.')

    @property
    def tipo(self) -> str:
        return 'metálica'

    @property
    def processo_construcao(self) -> str:
        return 'deslocamento'  # Steel piles are typically driven

    @property
    def cota_assentamento(self) -> int:
        return self._cota_assentamento

    @property
    def area_ponta(self) -> float:
        """
        Tip area depends on whether pile is open or closed-ended.

        For closed-ended: use full section area
        For open-ended tubular: use annular area (steel only)
        """
        if self.ponta_fechada:
            # For closed piles, use circumscribed area
            if self.perfil.tipo_perfil == 'tubular':
                # Full circular area
                d = self.perfil.diametro_externo / 1000  # mm to m
                return math.pi * (d / 2) ** 2
            # For H/I profiles, use rectangle area (d x bf)
            elif self.perfil.altura and self.perfil.largura:
                h = self.perfil.altura / 1000
                b = self.perfil.largura / 1000
                return h * b
        # Open-ended or structural area
        return self.perfil.area_m2

    @property
    def perimetro(self) -> float:
        return self.perfil.perimetro_m

    @property
    def secao_transversal(self) -> float:
        """Equivalent diameter for compatibility."""
        if self.perfil.tipo_perfil == 'tubular':
            return (self.perfil.diametro_externo or 0) / 1000
        elif self.perfil.altura:
            return self.perfil.altura / 1000
        return math.sqrt(self.area_ponta)

    @property
    def formato(self) -> Literal['circular', 'quadrada']:
        """
        Approximate shape for compatibility.

        Tubular -> circular
        HP, W, I, Box -> quadrada (treated as non-circular)
        """
        if self.perfil.tipo_perfil == 'tubular':
            return 'circular'
        return 'quadrada'

    def na_cota(self, nova_cota: int) -> 'EstacaMetalica':
        return replace(self, _cota_assentamento=nova_cota)


# =============================================================================
# PILE FACTORY
# =============================================================================


class EstacaFactory:
    """
    Factory for creating pile instances.

    Provides a clean API for creating different pile types with
    proper validation and defaults. Integrates with all pile catalogs.
    """

    # -------------------------------------------------------------------------
    # BASIC SHAPE CREATION
    # -------------------------------------------------------------------------

    @staticmethod
    def criar_circular(
        tipo: str,
        processo_construcao: str,
        diametro: float,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create a circular pile with custom dimensions."""
        return EstacaCircular(
            _tipo=tipo,
            _processo_construcao=processo_construcao,
            diametro=diametro,
            _cota_assentamento=cota_assentamento,
        )

    @staticmethod
    def criar_quadrada(
        tipo: str,
        processo_construcao: str,
        lado: float,
        cota_assentamento: int,
    ) -> EstacaQuadrada:
        """Create a square pile with custom dimensions."""
        return EstacaQuadrada(
            _tipo=tipo,
            _processo_construcao=processo_construcao,
            lado=lado,
            _cota_assentamento=cota_assentamento,
        )

    # -------------------------------------------------------------------------
    # STEEL PILE CREATION
    # -------------------------------------------------------------------------

    @staticmethod
    def criar_metalica(
        perfil: str | PerfilMetalico,
        cota_assentamento: int,
        ponta_fechada: bool = True,
    ) -> EstacaMetalica:
        """
        Create a steel pile with specific profile.

        Args:
            perfil: Profile name (from catalog) or PerfilMetalico instance.
            cota_assentamento: Installation depth.
            ponta_fechada: Whether pile tip is closed.

        Returns:
            EstacaMetalica instance.
        """
        if isinstance(perfil, str):
            if perfil not in CATALOGO_PERFIS_METALICOS:
                available = ', '.join(CATALOGO_PERFIS_METALICOS.keys())
                raise ValueError(
                    f'Perfil "{perfil}" não encontrado. '
                    f'Disponíveis: {available}'
                )
            perfil = CATALOGO_PERFIS_METALICOS[perfil]

        return EstacaMetalica(
            perfil=perfil,
            _cota_assentamento=cota_assentamento,
            ponta_fechada=ponta_fechada,
        )

    @staticmethod
    def criar_perfil_customizado(
        nome: str,
        tipo_perfil: Literal['HP', 'W', 'I', 'tubular', 'caixao'],
        area_cm2: float,
        perimetro_cm: float,
        **kwargs,
    ) -> PerfilMetalico:
        """
        Create a custom steel profile not in the catalog.

        Args:
            nome: Profile name/designation.
            tipo_perfil: Profile type.
            area_cm2: Section area in cm².
            perimetro_cm: Perimeter in cm.
            **kwargs: Additional properties (altura, largura, etc.)

        Returns:
            PerfilMetalico instance.
        """
        return PerfilMetalico(
            nome=nome,
            tipo_perfil=tipo_perfil,
            area_secao=area_cm2,
            perimetro=perimetro_cm,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # CATALOG-BASED CREATION
    # -------------------------------------------------------------------------

    @staticmethod
    def criar_de_catalogo(
        tipo_estaca: str,
        nome_perfil: str,
        cota_assentamento: int,
        **kwargs,
    ) -> EstacaBase:
        """
        Create a pile from any catalog profile.

        This is the unified method for creating piles from pre-defined
        configurations in any catalog.

        Args:
            tipo_estaca: Pile type ('pre_moldada', 'escavada', 'helice_continua',
                        'raiz', 'franki', 'omega', 'metalica').
            nome_perfil: Profile name from the catalog.
            cota_assentamento: Installation depth.
            **kwargs: Additional parameters specific to pile type.

        Returns:
            Appropriate pile instance.

        Example:
            estaca = EstacaFactory.criar_de_catalogo(
                'pre_moldada', 'CIRCULAR_330', 12
            )
        """
        from calculus_core.domain.pile_catalogs import (
            PerfilEscavada,
            PerfilFranki,
            PerfilHeliceContinua,
            PerfilOmega,
            PerfilPreMoldada,
            PerfilRaiz,
            obter_perfil,
        )

        tipo_norm = tipo_estaca.lower().replace(' ', '_').replace('-', '_')

        # Handle steel piles separately
        if tipo_norm in ('metalica', 'metálica'):
            ponta_fechada = kwargs.get('ponta_fechada', True)
            return EstacaFactory.criar_metalica(
                nome_perfil, cota_assentamento, ponta_fechada
            )

        # Get profile from catalog
        perfil = obter_perfil(tipo_estaca, nome_perfil)

        # Create appropriate pile type based on profile
        if isinstance(perfil, PerfilPreMoldada):
            if perfil.formato == 'circular':
                return EstacaCircular(
                    _tipo='pré_moldada',
                    _processo_construcao='deslocamento',
                    diametro=perfil.dimensao_principal,
                    _cota_assentamento=cota_assentamento,
                )
            else:
                return EstacaQuadrada(
                    _tipo='pré_moldada',
                    _processo_construcao='deslocamento',
                    lado=perfil.dimensao_principal,
                    _cota_assentamento=cota_assentamento,
                )

        if isinstance(perfil, PerfilEscavada):
            processo = (
                'escavada_bentonita'
                if perfil.tipo_execucao == 'com_fluido'
                else 'escavada'
            )
            return EstacaCircular(
                _tipo='escavada',
                _processo_construcao=processo,
                diametro=perfil.diametro,
                _cota_assentamento=cota_assentamento,
            )

        if isinstance(perfil, PerfilHeliceContinua):
            return EstacaCircular(
                _tipo='hélice_contínua',
                _processo_construcao='escavada',
                diametro=perfil.diametro,
                _cota_assentamento=cota_assentamento,
            )

        if isinstance(perfil, PerfilRaiz):
            return EstacaCircular(
                _tipo='raiz',
                _processo_construcao=(
                    'injetada'
                    if perfil.tipo_injecao == 'multipla'
                    else 'escavada'
                ),
                diametro=perfil.diametro_efetivo,
                _cota_assentamento=cota_assentamento,
            )

        if isinstance(perfil, PerfilFranki):
            # Franki uses expanded base area
            return EstacaCircular(
                _tipo='franki',
                _processo_construcao='deslocamento',
                diametro=perfil.diametro_base,  # Use expanded base diameter
                _cota_assentamento=cota_assentamento,
            )

        if isinstance(perfil, PerfilOmega):
            return EstacaCircular(
                _tipo='ômega',
                _processo_construcao='deslocamento',
                diametro=perfil.diametro,
                _cota_assentamento=cota_assentamento,
            )

        raise ValueError(f'Tipo de perfil não suportado: {type(perfil)}')

    @staticmethod
    def criar_pre_moldada(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaBase:
        """Create a precast pile from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'pre_moldada', nome_perfil, cota_assentamento
        )

    @staticmethod
    def criar_escavada(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create a bored pile from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'escavada', nome_perfil, cota_assentamento
        )

    @staticmethod
    def criar_helice_continua(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create a CFA pile from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'helice_continua', nome_perfil, cota_assentamento
        )

    @staticmethod
    def criar_raiz(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create a root pile (micropile) from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'raiz', nome_perfil, cota_assentamento
        )

    @staticmethod
    def criar_franki(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create a Franki pile from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'franki', nome_perfil, cota_assentamento
        )

    @staticmethod
    def criar_omega(
        nome_perfil: str,
        cota_assentamento: int,
    ) -> EstacaCircular:
        """Create an Omega pile from catalog."""
        return EstacaFactory.criar_de_catalogo(
            'omega', nome_perfil, cota_assentamento
        )

    # -------------------------------------------------------------------------
    # CATALOG INFORMATION
    # -------------------------------------------------------------------------

    @staticmethod
    def listar_tipos_estaca() -> list[str]:
        """List all available pile types with catalogs."""
        from calculus_core.domain.pile_catalogs import listar_tipos_estaca

        tipos = listar_tipos_estaca()
        tipos.append('metalica')
        return tipos

    @staticmethod
    def listar_perfis_por_tipo(tipo_estaca: str) -> list[str]:
        """List all profiles available for a pile type."""
        tipo_norm = tipo_estaca.lower().replace(' ', '_')

        if tipo_norm in ('metalica', 'metálica'):
            return list(CATALOGO_PERFIS_METALICOS.keys())

        from calculus_core.domain.pile_catalogs import listar_perfis_por_tipo

        return listar_perfis_por_tipo(tipo_estaca)

    @staticmethod
    def listar_perfis_disponiveis() -> list[str]:
        """List all available steel profiles in catalog (legacy)."""
        return list(CATALOGO_PERFIS_METALICOS.keys())

    @staticmethod
    def obter_perfil(nome: str) -> PerfilMetalico:
        """Get a steel profile from the catalog (legacy)."""
        if nome not in CATALOGO_PERFIS_METALICOS:
            raise ValueError(f'Perfil "{nome}" não encontrado.')
        return CATALOGO_PERFIS_METALICOS[nome]

    @staticmethod
    def obter_info_perfil(tipo_estaca: str, nome_perfil: str) -> dict:
        """
        Get detailed information about a catalog profile.

        Returns a dictionary with all profile properties.
        """
        tipo_norm = tipo_estaca.lower().replace(' ', '_')

        if tipo_norm in ('metalica', 'metálica'):
            perfil = CATALOGO_PERFIS_METALICOS.get(nome_perfil)
            if not perfil:
                raise ValueError(f'Perfil "{nome_perfil}" não encontrado.')
            return {
                'nome': perfil.nome,
                'tipo_perfil': perfil.tipo_perfil,
                'area_m2': perfil.area_m2,
                'perimetro_m': perfil.perimetro_m,
                'altura_mm': perfil.altura,
                'largura_mm': perfil.largura,
            }

        from calculus_core.domain.pile_catalogs import obter_perfil

        perfil = obter_perfil(tipo_estaca, nome_perfil)

        info = {'nome': perfil.nome}

        if hasattr(perfil, 'diametro'):
            info['diametro_m'] = perfil.diametro
        if hasattr(perfil, 'dimensao_principal'):
            info['dimensao_principal_m'] = perfil.dimensao_principal
        if hasattr(perfil, 'area'):
            info['area_m2'] = perfil.area
        if hasattr(perfil, 'perimetro'):
            info['perimetro_m'] = perfil.perimetro
        if hasattr(perfil, 'profundidade_maxima'):
            info['profundidade_maxima_m'] = perfil.profundidade_maxima
        if hasattr(perfil, 'capacidade_estrutural'):
            info['capacidade_estrutural_kN'] = perfil.capacidade_estrutural

        return info

    @staticmethod
    def resumo_catalogos() -> dict:
        """Get summary of all available catalogs."""
        from calculus_core.domain.pile_catalogs import resumo_catalogos

        resumo = resumo_catalogos()
        # Add steel profiles
        resumo['metalica'] = [
            {
                'nome': k,
                'descricao': v.nome,
                'area_m2': v.area_m2,
                'perimetro_m': v.perimetro_m,
            }
            for k, v in CATALOGO_PERFIS_METALICOS.items()
        ]
        return resumo
