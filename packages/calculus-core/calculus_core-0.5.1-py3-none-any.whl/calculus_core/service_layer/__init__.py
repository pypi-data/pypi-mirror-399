"""
Service Layer Package

Application services (use cases) that orchestrate domain operations.
"""

from .services import (
    BatchResult,
    CalculationRequest,
    CalculationResult,
    # Core classes
    CalculationService,
    calcular_todos_metodos_todas_estacas,
    # Batch calculation functions
    calcular_todos_metodos_uma_estaca,
    calcular_um_metodo_todas_estacas,
    # Single calculation functions
    calculate_pile_capacity,
    calculate_pile_capacity_by_depth,
    serializar_resultados,
)

__all__ = [
    # Core classes
    'CalculationService',
    'CalculationRequest',
    'CalculationResult',
    'BatchResult',
    # Simple API
    'calculate_pile_capacity',
    'calculate_pile_capacity_by_depth',
    # Batch API
    'calcular_todos_metodos_uma_estaca',
    'calcular_um_metodo_todas_estacas',
    'calcular_todos_metodos_todas_estacas',
    'serializar_resultados',
]
