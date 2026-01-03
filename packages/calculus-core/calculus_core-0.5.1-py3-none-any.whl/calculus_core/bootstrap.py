"""
Application Bootstrap - Composition Root

This module is the composition root where all dependencies are wired together.
It provides factory functions to create fully configured calculator instances.

Following the Cosmic Python principle of having a single place where
dependencies are composed, this makes the system:
- Easy to configure
- Easy to test (swap real implementations with mocks)
- Easy to understand (all wiring in one place)
"""

from calculus_core.domain.calculation import (
    MetodoCalculo,
)
from calculus_core.domain.method_registry import CalculationMethodRegistry
from calculus_core.service_layer import CalculationService

# =============================================================================
# CALCULATOR FACTORIES
# =============================================================================


def create_calculator(method_id: str) -> MetodoCalculo:
    """
    Create a calculator instance by its ID using the registry.

    This replaces individual factory functions, allowing the system to
    automatically support any method registered in the method_registry.
    """
    return CalculationMethodRegistry.create_calculator(method_id)


# =============================================================================
# SERVICE FACTORIES
# =============================================================================


def create_calculation_service(method: str) -> CalculationService:
    """
    Create a CalculationService for a specific method.

    Args:
        method: Method ID registered in CalculationMethodRegistry.

    Returns:
        Configured CalculationService instance.

    Raises:
        ValueError: If method name is not recognized.
    """
    try:
        calculator = create_calculator(method)
        return CalculationService(calculator)
    except ValueError as e:
        # Wrap or re-raise with helpful message
        available = ', '.join(CalculationMethodRegistry.list_ids())
        raise ValueError(
            f'Método desconhecido: {method}. Opções: {available}'
        ) from e


# =============================================================================
# PRE-CONFIGURED INSTANCES (for convenience)
# =============================================================================

# Lazy loading to avoid circular imports
_calculator_cache: dict[str, MetodoCalculo] = {}


def get_calculator_instance(method_id: str) -> MetodoCalculo:
    """Get a cached calculator instance by ID."""
    if method_id not in _calculator_cache:
        _calculator_cache[method_id] = create_calculator(method_id)
    return _calculator_cache[method_id]


def get_all_calculators() -> dict[str, MetodoCalculo]:
    """
    Get all available calculators.

    Returns:
        Dictionary mapping method names to calculator instances.
    """
    methods = CalculationMethodRegistry.list_all()
    result = {}

    for method_info in methods:
        try:
            instance = get_calculator_instance(method_info.id)
            # Use method name (human readable) as key for UI convenience,
            # or keep ID if strict compliance is needed.
            # The previous implementation used human readable names here.
            result[method_info.name] = instance
        except Exception:
            # If a calculator fails to instantiate, skip it but don't crash
            continue

    return result
