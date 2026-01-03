"""
Calculation Method Registry

This module provides a plugin-style registry for calculation methods.
New methods can be registered dynamically, making it easy to add
+12 or more methods without modifying core code.

Design Pattern: Plugin/Registry Pattern
"""

from dataclasses import dataclass
from typing import Callable

from calculus_core.domain.calculation.base import MetodoCalculo
from calculus_core.domain.soil_types import SoilMapperRegistry, SoilTypeMapper

# =============================================================================
# METHOD METADATA
# =============================================================================


@dataclass
class CalculationMethodInfo:
    """
    Metadata about a calculation method.

    Contains all information needed to display, configure, and
    instantiate a calculation method.
    """

    # Identification
    id: str  # Unique identifier (e.g., 'aoki_velloso_1975')
    name: str  # Display name (e.g., 'Aoki e Velloso (1975)')
    version: str  # Method version/year

    # Description
    description: str
    reference: str  # Bibliographic reference
    authors: list[str]

    # Capabilities
    supported_pile_types: list[str]
    supported_soil_types: list[str]

    # Factory
    calculator_factory: Callable[[], MetodoCalculo]
    soil_mapper: SoilTypeMapper | None = None

    # Constraints
    requires_reliable_spt: bool = False
    min_spt_depth: int = 2
    notes: str | None = None


# =============================================================================
# METHOD REGISTRY
# =============================================================================


class CalculationMethodRegistry:
    """
    Central registry for all calculation methods.

    This enables:
    1. Easy addition of new methods (register once, use everywhere)
    2. Discovery of available methods
    3. Filtering by capabilities (pile type, soil type, etc.)
    4. Consistent instantiation
    """

    _methods: dict[str, CalculationMethodInfo] = {}

    @classmethod
    def register(cls, method_info: CalculationMethodInfo) -> None:
        """
        Register a calculation method.

        Args:
            method_info: Complete method information.
        """
        cls._methods[method_info.id] = method_info

        # Also register soil mapper if provided
        if method_info.soil_mapper:
            SoilMapperRegistry.register(
                method_info.id, method_info.soil_mapper
            )

    @classmethod
    def get(cls, method_id: str) -> CalculationMethodInfo:
        """Get method information by ID."""
        if method_id not in cls._methods:
            available = ', '.join(cls._methods.keys())
            raise ValueError(
                f'Método "{method_id}" não encontrado. Disponíveis: {available}'
            )
        return cls._methods[method_id]

    @classmethod
    def create_calculator(cls, method_id: str) -> MetodoCalculo:
        """Create a calculator instance for a method."""
        info = cls.get(method_id)
        return info.calculator_factory()

    @classmethod
    def list_all(cls) -> list[CalculationMethodInfo]:
        """List all registered methods."""
        return list(cls._methods.values())

    @classmethod
    def list_ids(cls) -> list[str]:
        """List all method IDs."""
        return list(cls._methods.keys())

    @classmethod
    def list_by_pile_type(cls, pile_type: str) -> list[CalculationMethodInfo]:
        """List methods that support a specific pile type."""
        pile_type_norm = pile_type.lower().replace(' ', '_')
        return [
            m
            for m in cls._methods.values()
            if pile_type_norm in m.supported_pile_types
            or 'all' in m.supported_pile_types
        ]

    @classmethod
    def list_by_soil_type(cls, soil_type: str) -> list[CalculationMethodInfo]:
        """List methods that support a specific soil type."""
        soil_type_norm = soil_type.lower().replace(' ', '_')
        return [
            m
            for m in cls._methods.values()
            if soil_type_norm in m.supported_soil_types
            or 'all' in m.supported_soil_types
        ]

    @classmethod
    def is_registered(cls, method_id: str) -> bool:
        """Check if a method is registered."""
        return method_id in cls._methods

    @classmethod
    def unregister(cls, method_id: str) -> None:
        """Unregister a method (useful for testing)."""
        if method_id in cls._methods:
            del cls._methods[method_id]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered methods (useful for testing)."""
        cls._methods.clear()


# =============================================================================
# REGISTRATION DECORATOR
# =============================================================================


def register_method(
    method_id: str,
    name: str,
    version: str,
    description: str,
    reference: str,
    authors: list[str],
    supported_pile_types: list[str],
    supported_soil_types: list[str],
    soil_mapper: SoilTypeMapper | None = None,
    **kwargs,
):
    """
    Decorator to register a calculation method factory.

    Usage:
        @register_method(
            method_id='meu_metodo_2024',
            name='Meu Método (2024)',
            version='2024',
            description='Novo método de cálculo',
            reference='Silva, K. (2024). Novo Método.',
            authors=['Silva, K.'],
            supported_pile_types=['all'],
            supported_soil_types=['all'],
        )
        def create_meu_metodo():
            return MeuMetodoCalculator(...)
    """

    def decorator(factory_func: Callable[[], MetodoCalculo]):
        info = CalculationMethodInfo(
            id=method_id,
            name=name,
            version=version,
            description=description,
            reference=reference,
            authors=authors,
            supported_pile_types=supported_pile_types,
            supported_soil_types=supported_soil_types,
            calculator_factory=factory_func,
            soil_mapper=soil_mapper,
            **kwargs,
        )
        CalculationMethodRegistry.register(info)
        return factory_func

    return decorator


# =============================================================================
# REGISTER BUILT-IN METHODS
# =============================================================================


def _register_builtin_methods():
    """Register all built-in calculation methods."""
    from calculus_core.adapters.coefficients import (
        AokiVelloso1975Provider,
        AokiVellosoLaprovitera1988Provider,
        DecourtQuaresma1978Provider,
        Teixeira1996Provider,
    )
    from calculus_core.domain.calculation import (
        AokiVellosoCalculator,
        DecourtQuaresmaCalculator,
        TeixeiraCalculator,
    )
    from calculus_core.domain.soil_types import (
        AokiVellosoSoilMapper,
        DecourtQuaresmaSoilMapper,
        TeixeiraSoilMapper,
    )

    # Aoki-Velloso (1975)
    CalculationMethodRegistry.register(
        CalculationMethodInfo(
            id='aoki_velloso_1975',
            name='Aoki e Velloso (1975)',
            version='1975',
            description=(
                'Método semi-empírico baseado em correlações com o ensaio SPT '
                'para estacas cravadas e escavadas.'
            ),
            reference=(
                'AOKI, N.; VELLOSO, D. A. An approximate method to estimate '
                'the bearing capacity of piles. In: PANAMERICAN CONFERENCE ON '
                'SOIL MECHANICS AND FOUNDATION ENGINEERING, 5., 1975, Buenos Aires. '
                'Proceedings... Buenos Aires, 1975. v. 1, p. 367-376.'
            ),
            authors=['Aoki, N.', 'Velloso, D. A.'],
            supported_pile_types=[
                'franki',
                'metálica',
                'pré_moldada',
                'escavada',
                'raiz',
                'hélice_contínua',
                'ômega',
            ],
            supported_soil_types=['all'],
            calculator_factory=lambda: AokiVellosoCalculator(
                AokiVelloso1975Provider()
            ),
            soil_mapper=AokiVellosoSoilMapper(),
        )
    )

    # Aoki-Velloso (Laprovitera 1988)
    CalculationMethodRegistry.register(
        CalculationMethodInfo(
            id='aoki_velloso_laprovitera_1988',
            name='Aoki e Velloso (1975) por Laprovitera (1988)',
            version='1988',
            description=(
                'Revisão do método Aoki-Velloso com coeficientes atualizados '
                'por Laprovitera para solos brasileiros.'
            ),
            reference=(
                'LAPROVITERA, H. Reavaliação de Parâmetros de Projeto de '
                'Fundações Profundas à Luz das Modernas Técnicas de '
                'Instrumentação de Campo. 1988. Dissertação (Mestrado) - COPPE/UFRJ.'
            ),
            authors=['Laprovitera, H.'],
            supported_pile_types=[
                'franki',
                'metálica',
                'pré_moldada',
                'escavada',
                'raiz',
                'hélice_contínua',
                'ômega',
            ],
            supported_soil_types=['all'],
            calculator_factory=lambda: AokiVellosoCalculator(
                AokiVellosoLaprovitera1988Provider()
            ),
            soil_mapper=AokiVellosoSoilMapper(),
            notes='Inclui coeficientes alpha* para SPT não confiável.',
        )
    )

    # Décourt-Quaresma (1978)
    CalculationMethodRegistry.register(
        CalculationMethodInfo(
            id='decourt_quaresma_1978',
            name='Décourt e Quaresma (1978)',
            version='1978/1996',
            description=(
                'Método semi-empírico com coeficientes de correção α e β '
                'atualizados em 1996.'
            ),
            reference=(
                'DÉCOURT, L.; QUARESMA, A. R. Capacidade de carga de estacas '
                'a partir de valores de SPT. In: CONGRESSO BRASILEIRO DE '
                'MECÂNICA DOS SOLOS E ENGENHARIA DE FUNDAÇÕES, 6., 1978, '
                'Rio de Janeiro. Anais... Rio de Janeiro: ABMS, 1978. v. 1, p. 45-54.'
            ),
            authors=['Décourt, L.', 'Quaresma, A. R.'],
            supported_pile_types=[
                'cravada',
                'franki',
                'pré_moldada',
                'metálica',
                'ômega',
                'escavada',
                'escavada_bentonita',
                'hélice_contínua',
                'raiz',
                'injetada',
            ],
            supported_soil_types=['argila', 'silte', 'areia'],
            calculator_factory=lambda: DecourtQuaresmaCalculator(
                DecourtQuaresma1978Provider()
            ),
            soil_mapper=DecourtQuaresmaSoilMapper(),
        )
    )

    # Teixeira (1996)
    CalculationMethodRegistry.register(
        CalculationMethodInfo(
            id='teixeira_1996',
            name='Teixeira (1996)',
            version='1996',
            description=(
                'Método simplificado com intervalo específico para cálculo '
                'do Np baseado no diâmetro da estaca.'
            ),
            reference=(
                'TEIXEIRA, A. H. Projeto e execução de fundações. In: SEMINÁRIO '
                'DE ENGENHARIA DE FUNDAÇÕES ESPECIAIS E GEOTECNIA, 3., 1996, '
                'São Paulo. Anais... São Paulo: ABMS/ABEF, 1996. v. 1, p. 227-264.'
            ),
            authors=['Teixeira, A. H.'],
            supported_pile_types=[
                'pré_moldada',
                'metálica',
                'franki',
                'escavada',
                'raiz',
            ],
            supported_soil_types=['all'],
            calculator_factory=lambda: TeixeiraCalculator(
                Teixeira1996Provider()
            ),
            soil_mapper=TeixeiraSoilMapper(),
        )
    )


# Auto-register when module is imported
_register_builtin_methods()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_calculator(method_id: str) -> MetodoCalculo:
    """Convenience function to get a calculator by method ID."""
    return CalculationMethodRegistry.create_calculator(method_id)


def list_available_methods() -> list[dict]:
    """
    List all available methods with summary info.

    Returns list of dicts with id, name, version, description.
    """
    return [
        {
            'id': m.id,
            'name': m.name,
            'version': m.version,
            'description': m.description,
            'authors': m.authors,
        }
        for m in CalculationMethodRegistry.list_all()
    ]


def get_method_info(method_id: str) -> CalculationMethodInfo:
    """Get complete information about a method."""
    return CalculationMethodRegistry.get(method_id)
