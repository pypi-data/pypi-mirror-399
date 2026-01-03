"""
Soil Type System - Extensible Soil Classification

This module provides an abstraction for handling soil types across
different calculation methods. Each method may have its own soil
classification system, and this module handles the mapping.

Design Principles:
1. Each method defines its own valid soil types
2. A mapping layer translates between a canonical soil type and method-specific types
3. Methods can define fallback strategies for unsupported soils
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Protocol, runtime_checkable

# =============================================================================
# CANONICAL SOIL TYPES
# =============================================================================


class TipoSoloCanonical(Enum):
    """
    Canonical soil types representing the unified classification.

    This is the "lingua franca" for soil types across all methods.
    Each calculation method maps from these to their specific types.
    """

    # Primary types
    ARGILA = auto()
    SILTE = auto()
    AREIA = auto()

    # Clay variants
    ARGILA_ARENOSA = auto()
    ARGILA_ARENO_SILTOSA = auto()
    ARGILA_SILTOSA = auto()
    ARGILA_SILTO_ARENOSA = auto()

    # Silt variants
    SILTE_ARENOSO = auto()
    SILTE_ARENO_ARGILOSO = auto()
    SILTE_ARGILOSO = auto()
    SILTE_ARGILO_ARENOSO = auto()

    # Sand variants
    AREIA_SILTOSA = auto()
    AREIA_SILTO_ARGILOSA = auto()
    AREIA_ARGILOSA = auto()
    AREIA_ARGILO_SILTOSA = auto()
    AREIA_COM_PEDREGULHOS = auto()

    # Special types
    IMPENETRAVEL = auto()
    ROCHA = auto()
    ATERRO = auto()

    @classmethod
    def from_string(cls, nome: str) -> 'TipoSoloCanonical':
        """
        Create from string representation.

        Handles common variations in naming.
        """
        normalized = nome.upper().replace(' ', '_').replace('-', '_')

        # Direct match
        try:
            return cls[normalized]
        except KeyError:
            pass

        # Alias mapping
        aliases = {
            'PEDREGULHO': cls.AREIA_COM_PEDREGULHOS,
            'AREIA_PEDREGULHOSA': cls.AREIA_COM_PEDREGULHOS,
            'ROCHOSO': cls.ROCHA,
        }

        if normalized in aliases:
            return aliases[normalized]

        raise ValueError(f'Tipo de solo não reconhecido: {nome}')

    def to_string(self) -> str:
        """Convert to lowercase string representation."""
        return self.name.lower()


# =============================================================================
# SOIL MAPPER PROTOCOL
# =============================================================================


@runtime_checkable
class SoilTypeMapper(Protocol):
    """
    Protocol for soil type mapping between canonical and method-specific types.

    Each calculation method should implement this to handle its specific
    soil classification requirements.
    """

    def map_soil_type(
        self,
        canonical_type: TipoSoloCanonical | str,
        context: str | None = None,
    ) -> str:
        """
        Map a canonical soil type to method-specific type.

        Args:
            canonical_type: The canonical soil type.
            context: Optional context for contextual mapping (e.g., 'ponta', 'lateral').

        Returns:
            Method-specific soil type string.

        Raises:
            ValueError: If soil type cannot be mapped.
        """
        ...

    def supports_soil_type(
        self, canonical_type: TipoSoloCanonical | str
    ) -> bool:
        """Check if this mapper supports the given soil type."""
        ...

    def get_supported_types(self) -> list[TipoSoloCanonical]:
        """List all supported canonical soil types."""
        ...


# =============================================================================
# ABSTRACT SOIL MAPPER
# =============================================================================


class BaseSoilMapper(ABC):
    """
    Abstract base class for soil type mappers.

    Provides common functionality and enforces the mapping contract.
    """

    def __init__(
        self,
        mapping: dict[TipoSoloCanonical, str],
        fallback_mapping: dict[TipoSoloCanonical, TipoSoloCanonical]
        | None = None,
    ):
        """
        Initialize the mapper.

        Args:
            mapping: Direct mapping from canonical to method-specific types.
            fallback_mapping: Fallback to another canonical type if not found.
        """
        self._mapping = mapping
        self._fallback_mapping = fallback_mapping or {}

    def map_soil_type(
        self,
        canonical_type: TipoSoloCanonical | str,
        context: str | None = None,
    ) -> str:
        """Map canonical type to method-specific type."""
        # Convert string to enum if necessary
        if isinstance(canonical_type, str):
            canonical_type = TipoSoloCanonical.from_string(canonical_type)

        # Direct mapping
        if canonical_type in self._mapping:
            return self._mapping[canonical_type]

        # Fallback mapping
        if canonical_type in self._fallback_mapping:
            fallback_type = self._fallback_mapping[canonical_type]
            if fallback_type in self._mapping:
                return self._mapping[fallback_type]

        # Method-specific fallback
        return self._get_fallback(canonical_type, context)

    def supports_soil_type(
        self, canonical_type: TipoSoloCanonical | str
    ) -> bool:
        """Check if soil type is supported."""
        if isinstance(canonical_type, str):
            try:
                canonical_type = TipoSoloCanonical.from_string(canonical_type)
            except ValueError:
                return False

        return (
            canonical_type in self._mapping
            or canonical_type in self._fallback_mapping
        )

    def get_supported_types(self) -> list[TipoSoloCanonical]:
        """Get list of supported soil types."""
        supported = set(self._mapping.keys())
        supported.update(self._fallback_mapping.keys())
        return list(supported)

    @abstractmethod
    def _get_fallback(
        self,
        canonical_type: TipoSoloCanonical,
        context: str | None,
    ) -> str:
        """
        Get fallback for unsupported soil type.

        Subclasses should implement method-specific fallback logic.
        """
        pass


# =============================================================================
# METHOD-SPECIFIC MAPPERS
# =============================================================================


class AokiVellosoSoilMapper(BaseSoilMapper):
    """
    Soil mapper for Aoki-Velloso method.

    This method has specific coefficients for most soil types with
    minimal grouping.
    """

    def __init__(self):
        mapping = {
            TipoSoloCanonical.AREIA: 'areia',
            TipoSoloCanonical.AREIA_SILTOSA: 'areia_siltosa',
            TipoSoloCanonical.AREIA_SILTO_ARGILOSA: 'areia_silto_argilosa',
            TipoSoloCanonical.AREIA_ARGILOSA: 'areia_argilosa',
            TipoSoloCanonical.AREIA_ARGILO_SILTOSA: 'areia_argilo_siltosa',
            TipoSoloCanonical.SILTE: 'silte',
            TipoSoloCanonical.SILTE_ARENOSO: 'silte_arenoso',
            TipoSoloCanonical.SILTE_ARENO_ARGILOSO: 'silte_areno_argiloso',
            TipoSoloCanonical.SILTE_ARGILOSO: 'silte_argiloso',
            TipoSoloCanonical.SILTE_ARGILO_ARENOSO: 'silte_argilo_arenoso',
            TipoSoloCanonical.ARGILA: 'argila',
            TipoSoloCanonical.ARGILA_ARENOSA: 'argila_arenosa',
            TipoSoloCanonical.ARGILA_ARENO_SILTOSA: 'argila_areno_siltosa',
            TipoSoloCanonical.ARGILA_SILTOSA: 'argila_siltosa',
            TipoSoloCanonical.ARGILA_SILTO_ARENOSA: 'argila_silto_arenosa',
        }

        fallback = {
            # Sand with gravel maps to sand
            TipoSoloCanonical.AREIA_COM_PEDREGULHOS: TipoSoloCanonical.AREIA,
        }

        super().__init__(mapping, fallback)

    def _get_fallback(
        self,
        canonical_type: TipoSoloCanonical,
        context: str | None,
    ) -> str:
        """Use conservative sand for impenetrable, raise for others."""
        if canonical_type == TipoSoloCanonical.IMPENETRAVEL:
            return 'areia'  # Conservative assumption
        if canonical_type == TipoSoloCanonical.ROCHA:
            return 'areia'  # Conservative for rock

        raise ValueError(
            f'Tipo de solo não suportado pelo método Aoki-Velloso: {canonical_type}'
        )


class DecourtQuaresmaSoilMapper(BaseSoilMapper):
    """
    Soil mapper for Décourt-Quaresma method.

    This method groups soils into three main categories: argila, silte, areia.
    """

    def __init__(self):
        # All clay variants map to 'argila'
        mapping = {
            TipoSoloCanonical.ARGILA: 'argila',
            TipoSoloCanonical.ARGILA_ARENOSA: 'argila',
            TipoSoloCanonical.ARGILA_ARENO_SILTOSA: 'argila',
            TipoSoloCanonical.ARGILA_SILTOSA: 'argila',
            TipoSoloCanonical.ARGILA_SILTO_ARENOSA: 'argila',
            # All silt variants map to 'silte'
            TipoSoloCanonical.SILTE: 'silte',
            TipoSoloCanonical.SILTE_ARENOSO: 'silte',
            TipoSoloCanonical.SILTE_ARENO_ARGILOSO: 'silte',
            TipoSoloCanonical.SILTE_ARGILOSO: 'silte',
            TipoSoloCanonical.SILTE_ARGILO_ARENOSO: 'silte',
            # All sand variants map to 'areia'
            TipoSoloCanonical.AREIA: 'areia',
            TipoSoloCanonical.AREIA_SILTOSA: 'areia',
            TipoSoloCanonical.AREIA_SILTO_ARGILOSA: 'areia',
            TipoSoloCanonical.AREIA_ARGILOSA: 'areia',
            TipoSoloCanonical.AREIA_ARGILO_SILTOSA: 'areia',
            TipoSoloCanonical.AREIA_COM_PEDREGULHOS: 'areia',
        }

        super().__init__(mapping, {})

    def _get_fallback(
        self,
        canonical_type: TipoSoloCanonical,
        context: str | None,
    ) -> str:
        """Use sand for impenetrable, raise for others."""
        if canonical_type == TipoSoloCanonical.IMPENETRAVEL:
            return 'areia'
        if canonical_type == TipoSoloCanonical.ROCHA:
            return 'areia'

        raise ValueError(
            f'Tipo de solo não suportado pelo método Décourt-Quaresma: {canonical_type}'
        )


class TeixeiraSoilMapper(BaseSoilMapper):
    """
    Soil mapper for Teixeira method.

    This method has specific coefficients for combined soil types.
    """

    def __init__(self):
        mapping = {
            TipoSoloCanonical.ARGILA_SILTOSA: 'argila_siltosa',
            TipoSoloCanonical.ARGILA_SILTO_ARENOSA: 'argila_siltosa',  # Group
            TipoSoloCanonical.SILTE_ARGILOSO: 'silte_argiloso',
            TipoSoloCanonical.SILTE_ARGILO_ARENOSO: 'silte_argiloso',  # Group
            TipoSoloCanonical.ARGILA_ARENOSA: 'argila_arenosa',
            TipoSoloCanonical.ARGILA_ARENO_SILTOSA: 'argila_arenosa',  # Group
            TipoSoloCanonical.SILTE_ARENOSO: 'silte_arenoso',
            TipoSoloCanonical.SILTE_ARENO_ARGILOSO: 'silte_arenoso',  # Group
            TipoSoloCanonical.AREIA_ARGILOSA: 'areia_argilosa',
            TipoSoloCanonical.AREIA_ARGILO_SILTOSA: 'areia_argilosa',  # Group
            TipoSoloCanonical.AREIA_SILTOSA: 'areia_siltosa',
            TipoSoloCanonical.AREIA_SILTO_ARGILOSA: 'areia_siltosa',  # Group
            TipoSoloCanonical.AREIA: 'areia',
            TipoSoloCanonical.AREIA_COM_PEDREGULHOS: 'areia_com_pedregulhos',
        }

        # Fallbacks for primary types
        fallback = {
            TipoSoloCanonical.ARGILA: TipoSoloCanonical.ARGILA_SILTOSA,
            TipoSoloCanonical.SILTE: TipoSoloCanonical.SILTE_ARENOSO,
        }

        super().__init__(mapping, fallback)

    def _get_fallback(
        self,
        canonical_type: TipoSoloCanonical,
        context: str | None,
    ) -> str:
        """Use sand for impenetrable."""
        if canonical_type == TipoSoloCanonical.IMPENETRAVEL:
            return 'areia_com_pedregulhos'
        if canonical_type == TipoSoloCanonical.ROCHA:
            return 'areia_com_pedregulhos'

        raise ValueError(
            f'Tipo de solo não suportado pelo método Teixeira: {canonical_type}'
        )


# =============================================================================
# SOIL MAPPER REGISTRY
# =============================================================================


class SoilMapperRegistry:
    """
    Registry for soil type mappers.

    Provides a central place to register and retrieve mappers for
    different calculation methods.
    """

    _mappers: dict[str, SoilTypeMapper] = {}

    @classmethod
    def register(cls, method_name: str, mapper: SoilTypeMapper) -> None:
        """Register a mapper for a calculation method."""
        cls._mappers[method_name.lower()] = mapper

    @classmethod
    def get(cls, method_name: str) -> SoilTypeMapper:
        """Get mapper for a calculation method."""
        key = method_name.lower()
        if key not in cls._mappers:
            raise ValueError(
                f'Mapeador não encontrado para método: {method_name}'
            )
        return cls._mappers[key]

    @classmethod
    def has(cls, method_name: str) -> bool:
        """Check if mapper exists for method."""
        return method_name.lower() in cls._mappers

    @classmethod
    def list_methods(cls) -> list[str]:
        """List all registered methods."""
        return list(cls._mappers.keys())


# Register default mappers
SoilMapperRegistry.register('aoki_velloso', AokiVellosoSoilMapper())
SoilMapperRegistry.register('decourt_quaresma', DecourtQuaresmaSoilMapper())
SoilMapperRegistry.register('teixeira', TeixeiraSoilMapper())


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def map_soil_type(
    solo: str,
    method: str,
    context: str | None = None,
) -> str:
    """
    Convenience function to map a soil type string to method-specific type.

    Args:
        solo: Soil type as string.
        method: Calculation method name.
        context: Optional context for mapping.

    Returns:
        Method-specific soil type string.
    """
    mapper = SoilMapperRegistry.get(method)
    return mapper.map_soil_type(solo, context)


def is_soil_supported(solo: str, method: str) -> bool:
    """Check if a soil type is supported by a method."""
    mapper = SoilMapperRegistry.get(method)
    return mapper.supports_soil_type(solo)
