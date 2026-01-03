"""
Base Classes and Protocols for Calculation Strategies

This module defines the abstract interfaces (protocols) and base classes
for calculation methods. Following the Dependency Inversion Principle,
domain logic depends on abstractions, not concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from calculus_core.domain.model import Estaca, PerfilSPT
from calculus_core.domain.value_objects import ResultadoCalculo


@runtime_checkable
class CoefficientProvider(Protocol):
    """
    Protocol for coefficient data providers.

    This enables Dependency Inversion - the domain doesn't know where
    coefficients come from (memory, database, file, API).
    """

    def get_k(self, tipo_solo: str) -> float:
        """Get K coefficient for a soil type."""
        ...

    def get_alpha(self, tipo_solo: str, confiavel: bool = True) -> float:
        """Get alpha coefficient for a soil type."""
        ...

    def get_f1_f2(
        self, tipo_estaca: str, diametro: float | None = None
    ) -> tuple[float, float]:
        """Get F1 and F2 factors for a pile type."""
        ...


@runtime_checkable
class DecourtCoefficientProvider(Protocol):
    """
    Protocol for Décourt-Quaresma coefficient data providers.
    """

    def get_k(self, tipo_solo: str, processo_construcao: str) -> float:
        """Get K coefficient for soil type and construction process."""
        ...

    def get_alpha(self, tipo_solo: str, tipo_estaca: str) -> float:
        """Get alpha coefficient for soil type and pile type."""
        ...

    def get_beta(self, tipo_solo: str, tipo_estaca: str) -> float:
        """Get beta coefficient for soil type and pile type."""
        ...


@runtime_checkable
class TeixeiraCoefficientProvider(Protocol):
    """
    Protocol for Teixeira coefficient data providers.
    """

    def get_alpha(self, tipo_solo: str, tipo_estaca: str) -> float:
        """Get alpha coefficient for soil type and pile type."""
        ...

    def get_beta(self, tipo_estaca: str) -> float:
        """Get beta coefficient for pile type."""
        ...


class MetodoCalculo(ABC):
    """
    Abstract base class for calculation methods.

    Each method implementation receives its coefficient provider through
    dependency injection, enabling testability and extensibility.
    """

    @abstractmethod
    def calcular(
        self, perfil_spt: PerfilSPT, estaca: Estaca
    ) -> ResultadoCalculo:
        """
        Execute the load capacity calculation.

        Args:
            perfil_spt: SPT profile with soil layers.
            estaca: Pile characteristics.

        Returns:
            ResultadoCalculo with the calculation results.
        """
        pass

    @abstractmethod
    def cota_parada(self, perfil_spt: PerfilSPT) -> int:
        """
        Determine the stopping depth for iterative calculations.

        Args:
            perfil_spt: SPT profile.

        Returns:
            Maximum depth (cota) for calculations.
        """
        pass

    @staticmethod
    def calcular_carga_admissivel(
        resistencia_ponta: float,
        resistencia_lateral: float,
        fator_seguranca: float = 2.0,
    ) -> float:
        """
        Calculate allowable load capacity.

        Args:
            resistencia_ponta: Tip resistance.
            resistencia_lateral: Lateral resistance.
            fator_seguranca: Safety factor (default: 2.0).

        Returns:
            Allowable load capacity.
        """
        return (resistencia_ponta + resistencia_lateral) / fator_seguranca
