"""
Application Services

This module contains the application services (use cases) that
orchestrate domain operations. These are the primary entry points
for external callers.

Following Cosmic Python principles:
- Services have a clear purpose (use case)
- Services orchestrate domain objects
- Services don't contain business logic (that belongs in domain)
- Services can be easily tested with mocked dependencies
"""

from dataclasses import dataclass, field
from typing import Literal

from calculus_core.domain.calculation.base import MetodoCalculo
from calculus_core.domain.model import Estaca, PerfilSPT
from calculus_core.domain.value_objects import ResultadoCalculo
from calculus_core.utils.logging_config import get_logger


@dataclass
class CalculationRequest:
    """
    Value object representing a calculation request.

    Contains all parameters needed to execute a pile capacity calculation.
    """

    perfil_spt: PerfilSPT
    tipo_estaca: str
    processo_construcao: str
    formato: Literal['circular', 'quadrada']
    secao_transversal: float
    cota_assentamento: int | None = None  # None = calculate all depths
    estaca_prototype: Estaca | None = None  # For complex piles (e.g. catalogs)


@dataclass
class CalculationResult:
    """
    Value object representing the result of a calculation service call.

    Contains the calculation results and any errors that occurred.
    """

    success: bool
    resultados: list[ResultadoCalculo] = field(default_factory=list)
    error: str | None = None


class CalculationService:
    """
    Application service for pile capacity calculations.

    This service orchestrates the calculation process:
    1. Creates pile (Estaca) objects
    2. Invokes calculation methods
    3. Returns structured results


    Usage:
        service = CalculationService(aoki_velloso_calculator)
        result = service.calculate_all_depths(request)
    """

    def __init__(self, calculator: MetodoCalculo):
        """
        Initialize with a specific calculator.

        Args:
            calculator: The calculation method to use.
        """
        self._calculator = calculator
        self._logger = get_logger(f'{__name__}.{self.__class__.__name__}')

    def calculate_single_depth(
        self, request: CalculationRequest
    ) -> CalculationResult:
        """
        Calculate pile capacity at a single depth.

        Args:
            request: Calculation parameters with cota_assentamento set.

        Returns:
            CalculationResult with single result or error.
        """
        self._logger.info(
            'Iniciando cálculo único: estaca=%s, cota=%s',
            request.tipo_estaca,
            request.cota_assentamento,
        )

        if request.cota_assentamento is None:
            self._logger.error('Cota de assentamento não informada.')
            return CalculationResult(
                success=False,
                error='cota_assentamento é obrigatório para cálculo único.',
            )

        try:
            if request.estaca_prototype:
                # Use prototype but force specific depth
                estaca = request.estaca_prototype.na_cota(
                    request.cota_assentamento
                )
            else:
                estaca = Estaca(
                    tipo=request.tipo_estaca,
                    processo_construcao=request.processo_construcao,
                    formato=request.formato,
                    secao_transversal=request.secao_transversal,
                    cota_assentamento=request.cota_assentamento,
                )

            resultado = self._calculator.calcular(request.perfil_spt, estaca)
            self._logger.info('Cálculo realizado com sucesso.')

            return CalculationResult(
                success=True,
                resultados=[resultado],
            )

        except ValueError as e:
            self._logger.error('Erro de validação: %s', str(e))
            return CalculationResult(
                success=False,
                error=str(e),
            )

    def calculate_all_depths(
        self, request: CalculationRequest
    ) -> CalculationResult:
        """
        Calculate pile capacity at all valid depths.

        Args:
            request: Calculation parameters.

        Returns:
            CalculationResult with results for all depths or error.
        """
        self._logger.info(
            'Iniciando cálculo para todas as cotas: estaca=%s',
            request.tipo_estaca,
        )
        try:
            cota_parada = self._calculator.cota_parada(request.perfil_spt)
            self._logger.debug('Cota de parada identificada: %s', cota_parada)

            resultados = []

            for cota in range(1, cota_parada + 1):
                if request.estaca_prototype:
                    estaca = request.estaca_prototype.na_cota(cota)
                else:
                    estaca = Estaca(
                        tipo=request.tipo_estaca,
                        processo_construcao=request.processo_construcao,
                        formato=request.formato,
                        secao_transversal=request.secao_transversal,
                        cota_assentamento=cota,
                    )

                resultado = self._calculator.calcular(
                    request.perfil_spt, estaca
                )
                resultados.append(resultado)

            self._logger.info(
                'Cálculo finalizado para %d cotas.', len(resultados)
            )
            return CalculationResult(
                success=True,
                resultados=resultados,
            )

        except ValueError as e:
            self._logger.error('Erro durante cálculo: %s', str(e))
            return CalculationResult(
                success=False,
                error=str(e),
            )


# =============================================================================
# FUNCTIONAL API (for backwards compatibility and convenience)
# =============================================================================


def calculate_pile_capacity(
    calculator: MetodoCalculo,
    perfil_spt: PerfilSPT,
    tipo_estaca: str,
    processo_construcao: str,
    formato: Literal['circular', 'quadrada'],
    secao_transversal: float,
    cota_assentamento: int,
) -> dict:
    """
    Calculate pile capacity at a specific depth.

    This is a convenience function that wraps the CalculationService.

    Args:
        calculator: Calculation method to use.
        perfil_spt: SPT profile.
        tipo_estaca: Pile type.
        processo_construcao: Construction process.
        formato: Pile shape (circular or quadrada).
        secao_transversal: Cross-section dimension (m).
        cota_assentamento: Installation depth.

    Returns:
        Dictionary with calculation results.

    Raises:
        ValueError: If calculation fails.
    """
    estaca = Estaca(
        tipo=tipo_estaca,
        processo_construcao=processo_construcao,
        formato=formato,
        secao_transversal=secao_transversal,
        cota_assentamento=cota_assentamento,
    )

    resultado = calculator.calcular(perfil_spt, estaca)
    return resultado.to_dict()


def calculate_pile_capacity_by_depth(
    calculator: MetodoCalculo,
    perfil_spt: PerfilSPT,
    estaca: Estaca,  # Now accepts a prototype object (Estaca or EstacaBase)
) -> list[dict]:
    """
    Calculate pile capacity at all valid depths using a prototype pile.

    Args:
        calculator: Calculation method to use.
        perfil_spt: SPT profile.
        estaca: Prototype pile instance (will be cloned for each depth).

    Returns:
        List of dictionaries with calculation results for each depth.
    """
    cota_parada = calculator.cota_parada(perfil_spt)
    resultados = []

    for cota in range(1, cota_parada + 1):
        # Polymorphic creation of pile at new depth
        nova_estaca = estaca.na_cota(cota)

        resultado = calculator.calcular(perfil_spt, nova_estaca)
        resultados.append(resultado.to_dict())

    return resultados


# =============================================================================
# BATCH CALCULATION API
# =============================================================================


@dataclass
class BatchResult:
    """Result of a batch calculation."""

    metodo: str
    estaca: str
    cota: float
    resultado: ResultadoCalculo | None = None
    erro: str | None = None


def calcular_todos_metodos_uma_estaca(
    perfil_spt: PerfilSPT,
    estaca: Estaca,
) -> list[BatchResult]:
    """
    Calculate all available methods for a single pile.

    Use case: Compare all methods for a specific pile configuration.

    Args:
        perfil_spt: SPT profile.
        estaca: Pile to calculate.

    Returns:
        List of BatchResult with results from each method.

    Example:
        >>> estaca = Estaca('pré_moldada', 'deslocamento', 'circular', 0.3, 10)
        >>> resultados = calcular_todos_metodos_uma_estaca(perfil, estaca)
        >>> for r in resultados:
        ...     print(f"{r.metodo}: {r.resultado.capacidade_carga:.0f} kN")
    """
    from calculus_core.domain.method_registry import CalculationMethodRegistry

    resultados = []
    for method_id in CalculationMethodRegistry.list_ids():
        try:
            calc = CalculationMethodRegistry.create_calculator(method_id)
            resultado = calc.calcular(perfil_spt, estaca)
            resultados.append(
                BatchResult(
                    metodo=method_id,
                    estaca=estaca.tipo,
                    cota=estaca.cota_assentamento,
                    resultado=resultado,
                )
            )
        except Exception as e:
            resultados.append(
                BatchResult(
                    metodo=method_id,
                    estaca=estaca.tipo,
                    cota=estaca.cota_assentamento,
                    erro=str(e),
                )
            )

    return resultados


def calcular_um_metodo_todas_estacas(
    perfil_spt: PerfilSPT,
    metodo: str,
    cota_assentamento: float,
    tipos_estaca: list[str] | None = None,
    diametro_referencia: float = 0.40,
) -> list[BatchResult]:
    """
    Calculate one method for all available pile types.

    Selects a representative profile from each catalog closest to the
    reference diameter to ensure a fair comparison.

    Args:
        perfil_spt: SPT profile.
        metodo: Method ID to use.
        cota_assentamento: Installation depth.
        tipos_estaca: Optional list of pile types. If None, uses all.
        diametro_referencia: Target diameter (m) to select profiles.
                             Default is 0.40m (40cm).

    Returns:
        List of BatchResult with results for each pile type.

    Example:
        >>> resultados = calcular_um_metodo_todas_estacas(
        ...     perfil, 'decourt_quaresma_1978', 10, diametro_referencia=0.5
        ... )
    """
    from calculus_core.domain.method_registry import CalculationMethodRegistry
    from calculus_core.domain.pile_catalogs import (
        listar_perfis_por_tipo,
        listar_tipos_estaca,
        obter_perfil,
    )
    from calculus_core.domain.pile_types import EstacaFactory

    if tipos_estaca is None:
        tipos_estaca = listar_tipos_estaca()

    calc = CalculationMethodRegistry.create_calculator(metodo)
    resultados = []

    for tipo in tipos_estaca:
        try:
            # 1. Get all profiles for this type
            perfis = listar_perfis_por_tipo(tipo)
            if not perfis:
                continue

            # 2. Find best matching profile (closest diameter)
            melhor_perfil_nome = None
            menor_diff = float('inf')

            for nome in perfis:
                p = obter_perfil(tipo, nome)

                # Extract diameter from profile object
                d = getattr(
                    p,
                    'diametro',
                    getattr(
                        p,
                        'dimensao_principal',
                        getattr(p, 'diametro_fuste', None),
                    ),
                )

                if d is None:
                    continue

                diff = abs(d - diametro_referencia)
                if diff < menor_diff:
                    menor_diff = diff
                    melhor_perfil_nome = nome

            if not melhor_perfil_nome:
                # Fallback: take the first one if no diameter found
                melhor_perfil_nome = perfis[0]

            # 3. Create pile using factory
            estaca = EstacaFactory.criar_de_catalogo(
                tipo, melhor_perfil_nome, cota_assentamento
            )

            # 4. Calculate
            resultado = calc.calcular(perfil_spt, estaca)
            resultados.append(
                BatchResult(
                    metodo=metodo,
                    estaca=f'{estaca.tipo} ({melhor_perfil_nome})',
                    cota=cota_assentamento,
                    resultado=resultado,
                )
            )

        except Exception as e:
            resultados.append(
                BatchResult(
                    metodo=metodo,
                    estaca=tipo,
                    cota=cota_assentamento,
                    erro=f'Erro ao processar {tipo}: {str(e)}',
                )
            )

    return resultados


def calcular_todos_metodos_todas_estacas(
    perfil_spt: PerfilSPT,
    cota_assentamento: float,
    metodos: list[str] | None = None,
    tipos_estaca: list[str] | None = None,
    diametro_referencia: float = 0.40,
) -> list[BatchResult]:
    """
    Calculate all methods for all pile types (full matrix).

    Args:
        perfil_spt: SPT profile.
        cota_assentamento: Installation depth.
        metodos: Optional list of method IDs. If None, uses all.
        tipos_estaca: Optional list of pile types. If None, uses all.
        diametro_referencia: Target diameter to select profiles.

    Returns:
        List of BatchResult with all combinations.
    """
    from calculus_core.domain.method_registry import CalculationMethodRegistry

    if metodos is None:
        metodos = CalculationMethodRegistry.list_ids()

    resultados = []
    for metodo in metodos:
        batch = calcular_um_metodo_todas_estacas(
            perfil_spt,
            metodo,
            cota_assentamento,
            tipos_estaca,
            diametro_referencia,
        )
        resultados.extend(batch)

    return resultados


def serializar_resultados(resultados: list[BatchResult]) -> list[dict]:
    """
    Convert batch results to a list of flat dictionaries.

    This format is universal and can be easily consumed by any frontend
    or converted to libraries like pandas, polars, etc.

    Args:
        resultados: List of BatchResult objects.

    Returns:
        List of dictionaries with keys: metodo, estaca, cota,
        resistencia_ponta, resistencia_lateral, capacidade_carga,
        capacidade_carga_adm, and erro.

    Example:
        >>> resultados = calcular_todos_metodos_todas_estacas(perfil, 10)
        >>> dados = serializar_resultados(resultados)
        >>> # If using pandas:
        >>> # df = pd.DataFrame(dados)
    """
    dados = []
    for r in resultados:
        row = {
            'metodo': r.metodo,
            'estaca': r.estaca,
            'cota': r.cota,
            'erro': r.erro,
        }
        if r.resultado:
            row.update(
                {
                    'resistencia_ponta': r.resultado.resistencia_ponta,
                    'resistencia_lateral': r.resultado.resistencia_lateral,
                    'capacidade_carga': r.resultado.capacidade_carga,
                    'capacidade_carga_adm': r.resultado.capacidade_carga_adm,
                }
            )
        else:
            row.update(
                {
                    'resistencia_ponta': None,
                    'resistencia_lateral': None,
                    'capacidade_carga': None,
                    'capacidade_carga_adm': None,
                }
            )
        dados.append(row)

    return dados
