"""
Value Objects - Immutable Domain Concepts

Value objects are immutable and compared by their values rather than identity.
They represent concepts from the domain that have no lifecycle or identity.
"""

from dataclasses import dataclass
from enum import Enum


class FormatoEstaca(str, Enum):
    """Enumeration of valid pile shapes."""

    CIRCULAR = 'circular'
    QUADRADA = 'quadrada'


class ProcessoConstrucao(str, Enum):
    """Enumeration of construction processes."""

    DESLOCAMENTO = 'deslocamento'
    ESCAVADA = 'escavada'


@dataclass(frozen=True)
class TipoSolo:
    """
    Value object representing a soil type.

    This is immutable and validated at construction time.
    """

    nome: str

    def __post_init__(self):
        if not self.nome or not self.nome.strip():
            raise ValueError('O nome do tipo de solo não pode ser vazio.')

    @property
    def normalizado(self) -> str:
        """Return normalized soil type name."""
        return self.nome.lower().replace(' ', '_').replace('-', '_')


@dataclass(frozen=True)
class ResultadoCalculo:
    """
    Immutable result of a single load capacity calculation.

    Contains the complete output of a calculation for a specific
    pile installation depth (cota).
    """

    cota: int
    resistencia_ponta: float
    resistencia_lateral: float
    capacidade_carga: float
    capacidade_carga_adm: float

    def __post_init__(self):
        if self.cota < 1:
            raise ValueError('Cota deve ser >= 1.')
        if self.resistencia_ponta < 0:
            raise ValueError('Resistência de ponta não pode ser negativa.')
        if self.resistencia_lateral < 0:
            raise ValueError('Resistência lateral não pode ser negativa.')

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'cota': self.cota,
            'resistencia_ponta': self.resistencia_ponta,
            'resistencia_lateral': self.resistencia_lateral,
            'capacidade_carga': self.capacidade_carga,
            'capacidade_carga_adm': self.capacidade_carga_adm,
        }


@dataclass(frozen=True)
class FatoresF1F2:
    """Value object for F1 and F2 factors."""

    f1: float
    f2: float

    def __post_init__(self):
        if self.f1 <= 0 or self.f2 <= 0:
            raise ValueError('Fatores F1 e F2 devem ser positivos.')


@dataclass(frozen=True)
class CoeficienteSolo:
    """
    Value object for soil coefficients used in calculations.

    Contains K (kPa), alpha percentage, and optional alpha_star for
    unreliable SPT profiles.
    """

    k_kpa: float
    alpha_perc: float
    alpha_star_perc: float | None = None

    def __post_init__(self):
        if self.k_kpa <= 0:
            raise ValueError('K deve ser positivo.')
        if self.alpha_perc <= 0:
            raise ValueError('Alpha deve ser positivo.')

    @property
    def alpha(self) -> float:
        """Return alpha as a decimal (not percentage)."""
        return self.alpha_perc / 100

    @property
    def alpha_star(self) -> float | None:
        """Return alpha_star as a decimal (not percentage)."""
        if self.alpha_star_perc is None:
            return None
        return self.alpha_star_perc / 100

    def get_alpha(self, confiavel: bool = True) -> float:
        """
        Get the appropriate alpha value based on SPT reliability.

        Args:
            confiavel: Whether the SPT profile is reliable.

        Returns:
            Alpha value as a decimal.
        """
        if not confiavel and self.alpha_star is not None:
            return self.alpha_star
        return self.alpha
