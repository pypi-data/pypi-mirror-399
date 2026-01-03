"""
Domain Layer - Pure Business Logic

Contains entities, value objects, and calculation strategies for foundation
load capacity calculations. This layer is completely independent of any
external frameworks or infrastructure concerns.

Modules:
- model: Core entities (Estaca, PerfilSPT, MedidaSPT)
- value_objects: Immutable domain concepts (ResultadoCalculo, TipoSolo)
- calculation: Method implementations (Aoki-Velloso, Décourt-Quaresma, etc.)
- pile_types: Specific pile implementations and catalogs
- soil_types: Soil type mapping between methods
- soil_investigation: CPT profiles and CPT-SPT conversion
- method_registry: Plugin registry for calculation methods
"""

# Core entities
# Method registry
from .method_registry import (
    CalculationMethodInfo,
    CalculationMethodRegistry,
    get_calculator,
    get_method_info,
    list_available_methods,
    register_method,
)
from .model import Estaca, MedidaSPT, PerfilSPT
from .pile_catalogs import (
    CATALOGO_ESCAVADAS,
    CATALOGO_FRANKI,
    CATALOGO_HELICE_CONTINUA,
    CATALOGO_OMEGA,
    CATALOGO_PRE_MOLDADAS,
    CATALOGO_RAIZ,
    PerfilEscavada,
    PerfilFranki,
    PerfilHeliceContinua,
    PerfilOmega,
    PerfilPreMoldada,
    PerfilRaiz,
    buscar_perfil_por_diametro,
    listar_perfis_por_tipo,
    listar_tipos_estaca,
    obter_perfil,
    resumo_catalogos,
)

# Pile types and catalogs
from .pile_types import (
    CATALOGO_PERFIS_METALICOS,
    EstacaBase,
    EstacaCircular,
    EstacaFactory,
    EstacaMetalica,
    EstacaQuadrada,
    PerfilMetalico,
)

# Soil investigation (CPT, conversions)
from .soil_investigation import (
    ConversionRegistry,
    CPTtoSPTConverter,
    CPTtoSPTCorrelation,
    MedidaCPT,
    PerfilCPT,
    SoilTestType,
    converter_cpt_para_spt,
    listar_correlacoes_cpt_spt,
    obter_info_correlacao,
)

# Soil type system
from .soil_types import (
    AokiVellosoSoilMapper,
    BaseSoilMapper,
    DecourtQuaresmaSoilMapper,
    SoilMapperRegistry,
    SoilTypeMapper,
    TeixeiraSoilMapper,
    TipoSoloCanonical,
    is_soil_supported,
    map_soil_type,
)

# Value objects
from .value_objects import (
    CoeficienteSolo,
    FatoresF1F2,
    ResultadoCalculo,
    TipoSolo,
)

__all__ = [
    # Core entities
    'Estaca',
    'MedidaSPT',
    'PerfilSPT',
    # Value objects
    'ResultadoCalculo',
    'TipoSolo',
    'CoeficienteSolo',
    'FatoresF1F2',
    # Pile types
    'EstacaBase',
    'EstacaCircular',
    'EstacaQuadrada',
    'EstacaMetalica',
    'PerfilMetalico',
    'EstacaFactory',
    'CATALOGO_PERFIS_METALICOS',
    # Pile catalogs
    'PerfilPreMoldada',
    'PerfilEscavada',
    'PerfilHeliceContinua',
    'PerfilRaiz',
    'PerfilFranki',
    'PerfilOmega',
    'CATALOGO_PRE_MOLDADAS',
    'CATALOGO_ESCAVADAS',
    'CATALOGO_HELICE_CONTINUA',
    'CATALOGO_RAIZ',
    'CATALOGO_FRANKI',
    'CATALOGO_OMEGA',
    'listar_tipos_estaca',
    'listar_perfis_por_tipo',
    'obter_perfil',
    'buscar_perfil_por_diametro',
    'resumo_catalogos',
    # Soil type system
    'TipoSoloCanonical',
    'SoilTypeMapper',
    'BaseSoilMapper',
    'AokiVellosoSoilMapper',
    'DecourtQuaresmaSoilMapper',
    'TeixeiraSoilMapper',
    'SoilMapperRegistry',
    'map_soil_type',
    'is_soil_supported',
    # Soil investigation (CPT)
    'MedidaCPT',
    'PerfilCPT',
    'SoilTestType',
    'CPTtoSPTConverter',
    'CPTtoSPTCorrelation',
    'ConversionRegistry',
    'converter_cpt_para_spt',
    'listar_correlacoes_cpt_spt',
    'obter_info_correlacao',
    # Method registry
    'CalculationMethodInfo',
    'CalculationMethodRegistry',
    'register_method',
    'get_calculator',
    'list_available_methods',
    'get_method_info',
]
