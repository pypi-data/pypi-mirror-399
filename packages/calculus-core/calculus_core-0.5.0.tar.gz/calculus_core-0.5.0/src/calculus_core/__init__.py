"""
Calculus-Core - Foundation Load Capacity Calculator

A library for calculating foundation pile load capacity using
semi-empirical methods from Brazilian geotechnical literature.

Supported Methods:
- Aoki-Velloso (1975)
- Aoki-Velloso with Laprovitera corrections (1988)
- Décourt-Quaresma (1978)
- Teixeira (1996)

Quick Start:
    from calculus_core import create_aoki_velloso_1975, Estaca, PerfilSPT

    # Create SPT profile
    perfil = PerfilSPT()
    perfil.adicionar_medidas([
        (1.0, 3, 'argila_arenosa'),
        (2.0, 5, 'argila_arenosa'),
        (3.0, 8, 'areia'),
    ])

    # Create pile
    estaca = Estaca(
        tipo='pré_moldada',
        processo_construcao='deslocamento',
        formato='circular',
        secao_transversal=0.3,
        cota_assentamento=3.0,
    )

    # Calculate
    calculator = create_aoki_velloso_1975()
    resultado = calculator.calcular(perfil, estaca)
    print(resultado.to_dict())

Using Pre-defined Pile Catalogs:
    from calculus_core.domain import EstacaFactory

    # Create from catalog
    estaca = EstacaFactory.criar_helice_continua('HELICE_500', cota=15)
    estaca = EstacaFactory.criar_metalica('HP_310x79', cota=20)
"""

__version__ = '0.5.0'

# =============================================================================
# PUBLIC API
# =============================================================================

# Domain - Core Entities
# Adapters - Coefficient Providers
from calculus_core.adapters.coefficients import (
    AokiVelloso1975Provider,
    AokiVellosoLaprovitera1988Provider,
    DecourtQuaresma1978Provider,
    Teixeira1996Provider,
)

# Bootstrap - Factory Functions
from calculus_core.bootstrap import (
    create_calculation_service,
    create_calculator,  # [NEW]
    get_all_calculators,
    get_calculator_instance,  # [NEW]
)

# Domain - Calculation Strategies
from calculus_core.domain.calculation import (
    AokiVellosoCalculator,
    DecourtQuaresmaCalculator,
    MetodoCalculo,
    TeixeiraCalculator,
)
from calculus_core.domain.model import Estaca, MedidaSPT, PerfilSPT

# Domain - Value Objects
from calculus_core.domain.value_objects import (
    CoeficienteSolo,
    FatoresF1F2,
    ResultadoCalculo,
    TipoSolo,
)

# Service Layer
from calculus_core.service_layer import (
    BatchResult,
    CalculationRequest,
    CalculationResult,
    CalculationService,
    calcular_todos_metodos_todas_estacas,
    calcular_todos_metodos_uma_estaca,
    calcular_um_metodo_todas_estacas,
    calculate_pile_capacity,
    calculate_pile_capacity_by_depth,
    serializar_resultados,
)

__all__ = [
    # Version
    '__version__',
    # Domain - Entities
    'Estaca',
    'MedidaSPT',
    'PerfilSPT',
    # Domain - Value Objects
    'ResultadoCalculo',
    'TipoSolo',
    'CoeficienteSolo',
    'FatoresF1F2',
    # Domain - Calculators
    'MetodoCalculo',
    'AokiVellosoCalculator',
    'DecourtQuaresmaCalculator',
    'TeixeiraCalculator',
    # Adapters - Coefficient Providers
    'AokiVelloso1975Provider',
    'AokiVellosoLaprovitera1988Provider',
    'DecourtQuaresma1978Provider',
    'Teixeira1996Provider',
    # Bootstrap - Factories
    'create_calculator',  # [NEW]
    'get_calculator_instance',  # [NEW]
    'get_all_calculators',
    'create_calculation_service',
    # Services
    'CalculationService',
    'CalculationRequest',
    'CalculationResult',
    'calculate_pile_capacity',
    'calculate_pile_capacity_by_depth',
    # Batch API
    'BatchResult',
    'calcular_todos_metodos_uma_estaca',
    'calcular_um_metodo_todas_estacas',
    'calcular_todos_metodos_todas_estacas',
    'serializar_resultados',
]
