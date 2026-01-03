"""
Soil Investigation Abstractions

This module provides a unified interface for different types of soil investigation
tests (SPT, CPT, DMT, etc.) and conversion mechanisms between them.

Architecture:
- SoilProfile: Abstract base for all soil investigation data
- TestMeasurement: Abstract base for individual measurements
- ProfileConverter: Protocol for converting between profile types
- ConversionRegistry: Registry for available conversion strategies

This design allows:
1. Using CPT data directly with CPT-specific calculation methods
2. Converting CPT to equivalent SPT for use with traditional methods
3. Adding new test types without modifying existing code
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Protocol, TypeVar

# =============================================================================
# ENUMS
# =============================================================================


class SoilTestType(Enum):
    """Types of soil investigation tests."""

    SPT = 'spt'  # Standard Penetration Test
    CPT = 'cpt'  # Cone Penetration Test
    CPTU = 'cptu'  # Piezocone Test (CPT with pore pressure)
    DMT = 'dmt'  # Dilatometer Test
    PMT = 'pmt'  # Pressuremeter Test
    VANE = 'vane'  # Vane Shear Test


# =============================================================================
# ABSTRACT MEASUREMENT
# =============================================================================


@dataclass
class BaseMeasurement(ABC):
    """
    Abstract base class for soil test measurements.

    All test types share a depth attribute but have different
    measured values (N_SPT, qc, fs, etc.).
    """

    profundidade: float

    def __post_init__(self):
        if self.profundidade < 0:
            raise ValueError('Profundidade não pode ser negativa.')
        self.profundidade = round(self.profundidade, 3)

    @property
    @abstractmethod
    def test_type(self) -> SoilTestType:
        """Return the type of test this measurement belongs to."""
        ...

    @property
    @abstractmethod
    def primary_value(self) -> float:
        """
        Return the primary measured value for this test type.

        For SPT: N_SPT
        For CPT: qc (tip resistance)
        """
        ...


# =============================================================================
# CPT MEASUREMENT
# =============================================================================


@dataclass
class MedidaCPT(BaseMeasurement):
    """
    Measurement from a Cone Penetration Test (CPT).

    Attributes:
        profundidade: Depth in meters.
        qc: Cone tip resistance in MPa.
        fs: Sleeve friction in kPa.
        Rf: Friction ratio (fs/qc * 100) in %.
        u2: Pore pressure behind cone tip in kPa (optional, for CPTu).
    """

    qc: float  # Tip resistance (MPa)
    fs: float  # Sleeve friction (kPa)
    Rf: float | None = None  # Friction ratio (%)
    u2: float | None = None  # Pore pressure (kPa, for CPTu)

    def __post_init__(self):
        super().__post_init__()
        if self.qc < 0:
            raise ValueError('qc não pode ser negativo.')
        if self.fs < 0:
            raise ValueError('fs não pode ser negativo.')
        # Calculate Rf if not provided
        if self.Rf is None and self.qc > 0:
            self.Rf = (
                self.fs / (self.qc * 1000)
            ) * 100  # qc in MPa, fs in kPa

    @property
    def test_type(self) -> SoilTestType:
        return SoilTestType.CPTU if self.u2 is not None else SoilTestType.CPT

    @property
    def primary_value(self) -> float:
        return self.qc

    @property
    def qc_kpa(self) -> float:
        """Return qc in kPa."""
        return self.qc * 1000

    @property
    def is_cohesive(self) -> bool:
        """
        Estimate if soil is cohesive based on friction ratio.

        Rf > 3-4% typically indicates cohesive soil.
        """
        if self.Rf is None:
            return False
        return self.Rf > 3.5

    def __repr__(self) -> str:
        return (
            f'MedidaCPT(prof={self.profundidade}m, '
            f'qc={self.qc}MPa, fs={self.fs}kPa, Rf={self.Rf:.1f}%)'
        )


# =============================================================================
# CPT PROFILE
# =============================================================================


class PerfilCPT:
    """
    Aggregate representing a complete CPT (Cone Penetration Test) profile.

    CPT provides continuous measurements every few centimeters, giving
    high-resolution soil stratigraphy data.

    Attributes:
        nome_sondagem: Test identification name.
        intervalo_padrao: Standard measurement interval in meters.
    """

    def __init__(
        self,
        nome_sondagem: str = 'CPT-01',
        intervalo_padrao: float = 0.02,  # CPT typically every 2cm
    ):
        self.nome_sondagem = nome_sondagem
        self.intervalo_padrao = intervalo_padrao
        self._medidas: list[MedidaCPT] = []
        self._profundidades_cache: list[float] = []

    @property
    def medidas(self) -> list[MedidaCPT]:
        """Return a copy of the measurements list."""
        return list(self._medidas)

    @property
    def test_type(self) -> SoilTestType:
        """Return the test type."""
        return SoilTestType.CPT

    def _rebuild_cache(self) -> None:
        """Rebuild the depth lookup cache."""
        self._profundidades_cache = [m.profundidade for m in self._medidas]

    def adicionar_medida(
        self,
        profundidade: float,
        qc: float,
        fs: float,
        Rf: float | None = None,
        u2: float | None = None,
    ) -> None:
        """Add a single CPT measurement."""
        medida = MedidaCPT(profundidade, qc, fs, Rf, u2)
        self._medidas.append(medida)
        self._medidas.sort(key=lambda x: x.profundidade)
        self._rebuild_cache()

    def adicionar_medidas(
        self,
        dados: list[tuple[float, float, float]]
        | list[tuple[float, float, float, float]]
        | list[tuple[float, float, float, float, float]],
    ) -> None:
        """
        Add multiple CPT measurements at once.

        Args:
            dados: List of tuples:
                - (profundidade, qc, fs)
                - (profundidade, qc, fs, Rf)
                - (profundidade, qc, fs, Rf, u2)
        """
        for item in dados:
            if len(item) == 3:
                prof, qc, fs = item
                Rf, u2 = None, None
            elif len(item) == 4:
                prof, qc, fs, Rf = item
                u2 = None
            else:
                prof, qc, fs, Rf, u2 = item

            medida = MedidaCPT(prof, qc, fs, Rf, u2)
            self._medidas.append(medida)

        self._medidas.sort(key=lambda x: x.profundidade)
        self._rebuild_cache()

    def obter_medida(self, profundidade: float) -> MedidaCPT:
        """Get the CPT measurement closest to specified depth."""
        if not self._medidas:
            raise ValueError('Nenhuma medida registrada no perfil CPT.')

        return min(
            self._medidas,
            key=lambda x: abs(x.profundidade - profundidade),
        )

    def obter_qc_intervalo(
        self,
        prof_inicio: float,
        prof_fim: float,
        metodo: str = 'media',
    ) -> float:
        """Get aggregate qc for a depth interval."""
        if prof_inicio > prof_fim:
            prof_inicio, prof_fim = prof_fim, prof_inicio

        medidas_intervalo = [
            m
            for m in self._medidas
            if prof_inicio <= m.profundidade <= prof_fim
        ]

        if not medidas_intervalo:
            return self.obter_medida(prof_inicio).qc

        valores = [m.qc for m in medidas_intervalo]

        if metodo == 'media':
            return sum(valores) / len(valores)
        elif metodo == 'minimo':
            return min(valores)
        elif metodo == 'maximo':
            return max(valores)

        return sum(valores) / len(valores)

    @property
    def profundidade_minima(self) -> float:
        """Return the minimum depth in the profile."""
        if not self._medidas:
            raise ValueError('Nenhuma medida registrada.')
        return self._medidas[0].profundidade

    @property
    def profundidade_maxima(self) -> float:
        """Return the maximum depth in the profile."""
        if not self._medidas:
            raise ValueError('Nenhuma medida registrada.')
        return self._medidas[-1].profundidade

    def __repr__(self) -> str:
        if self._medidas:
            return (
                f'PerfilCPT(nome={self.nome_sondagem!r}, '
                f'medidas={len(self._medidas)}, '
                f'prof=[{self.profundidade_minima:.1f}-'
                f'{self.profundidade_maxima:.1f}m])'
            )
        return f'PerfilCPT(nome={self.nome_sondagem!r}, medidas=0)'

    def __len__(self) -> int:
        return len(self._medidas)

    def __getitem__(self, index: int) -> MedidaCPT:
        return self._medidas[index]

    def __iter__(self):
        return iter(self._medidas)


# =============================================================================
# SOIL PROFILE PROTOCOL
# =============================================================================

# Type variable for measurements
M = TypeVar('M', bound=BaseMeasurement)


class SoilProfile(Protocol[M]):
    """
    Protocol defining common interface for all soil investigation profiles.

    Any profile type (SPT, CPT, DMT) should implement this interface
    to be usable with the conversion system.
    """

    nome_sondagem: str

    @property
    def test_type(self) -> SoilTestType:
        """Return the type of test."""
        ...

    @property
    def profundidade_minima(self) -> float:
        """Return minimum depth."""
        ...

    @property
    def profundidade_maxima(self) -> float:
        """Return maximum depth."""
        ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[M]: ...


# =============================================================================
# PROFILE CONVERTER PROTOCOL
# =============================================================================


class ProfileConverter(Protocol):
    """
    Protocol for profile conversion strategies.

    Implementations convert between different test types,
    e.g., CPT to equivalent SPT.
    """

    @property
    def source_type(self) -> SoilTestType:
        """Type of input profile."""
        ...

    @property
    def target_type(self) -> SoilTestType:
        """Type of output profile."""
        ...

    def convert(self, source_profile: SoilProfile) -> SoilProfile:
        """Convert source profile to target type."""
        ...


# =============================================================================
# CPT TO SPT CONVERSION STRATEGIES
# =============================================================================


@dataclass
class CPTtoSPTCorrelation:
    """
    Parameters for CPT to SPT correlation.

    N_SPT = qc / k

    Where k (in kPa/blow) varies by soil type:
    - Clays: k = 100 - 200 (typically 150)
    - Silts: k = 200 - 300 (typically 250)
    - Sands: k = 350 - 500 (typically 400)
    - Gravels: k = 500 - 800 (typically 600)

    Based on Robertson et al. (1983), Aoki & Velloso (1975), etc.
    """

    nome: str
    k_argila: float = 150.0  # kPa/blow
    k_silte: float = 250.0  # kPa/blow
    k_areia: float = 400.0  # kPa/blow
    k_pedregulho: float = 600.0  # kPa/blow
    referencia: str = ''


# Pre-defined correlations (k in kPa/blow)
CORRELACAO_ROBERTSON_1983 = CPTtoSPTCorrelation(
    nome='Robertson (1983)',
    k_argila=150.0,
    k_silte=200.0,
    k_areia=400.0,
    k_pedregulho=500.0,
    referencia='Robertson, P.K. (1983). In-situ testing and its application.',
)

CORRELACAO_AOKI_VELLOSO_1975 = CPTtoSPTCorrelation(
    nome='Aoki-Velloso (1975)',
    k_argila=200.0,
    k_silte=250.0,
    k_areia=350.0,
    k_pedregulho=550.0,
    referencia='Aoki, N. e Velloso, D.A. (1975). Correlação CPT-SPT.',
)

CORRELACAO_DECOURT_1995 = CPTtoSPTCorrelation(
    nome='Décourt (1995)',
    k_argila=250.0,
    k_silte=300.0,
    k_areia=450.0,
    k_pedregulho=600.0,
    referencia='Décourt, L. (1995). Prediction of load-settlement.',
)

CATALOGOS_CORRELACAO_CPT_SPT = {
    'robertson_1983': CORRELACAO_ROBERTSON_1983,
    'aoki_velloso_1975': CORRELACAO_AOKI_VELLOSO_1975,
    'decourt_1995': CORRELACAO_DECOURT_1995,
}


class CPTtoSPTConverter:
    """
    Converts CPT profile to equivalent SPT profile.

    Uses qc/N correlations based on soil type inferred from
    friction ratio (Rf).

    Usage:
        converter = CPTtoSPTConverter(CORRELACAO_ROBERTSON_1983)
        perfil_spt = converter.convert(perfil_cpt)

        # Or use factory:
        perfil_spt = converter.convert(perfil_cpt, intervalo=1.0)
    """

    def __init__(
        self,
        correlacao: CPTtoSPTCorrelation | None = None,
        nome_correlacao: str | None = None,
    ):
        """
        Initialize converter.

        Args:
            correlacao: Correlation parameters object.
            nome_correlacao: Name of pre-defined correlation to use.
        """
        if correlacao is not None:
            self._correlacao = correlacao
        elif nome_correlacao is not None:
            if nome_correlacao not in CATALOGOS_CORRELACAO_CPT_SPT:
                available = ', '.join(CATALOGOS_CORRELACAO_CPT_SPT.keys())
                raise ValueError(
                    f'Correlação desconhecida: {nome_correlacao}. '
                    f'Disponíveis: {available}'
                )
            self._correlacao = CATALOGOS_CORRELACAO_CPT_SPT[nome_correlacao]
        else:
            self._correlacao = CORRELACAO_ROBERTSON_1983

    @property
    def source_type(self) -> SoilTestType:
        return SoilTestType.CPT

    @property
    def target_type(self) -> SoilTestType:
        return SoilTestType.SPT

    @property
    def correlacao(self) -> CPTtoSPTCorrelation:
        return self._correlacao

    def inferir_tipo_solo(self, medida: MedidaCPT) -> str:
        """
        Infer soil type from CPT measurement using Robertson chart zones.

        Based on normalized cone resistance and friction ratio.
        Simplified version using Rf only.
        """
        if medida.Rf is None:
            return 'areia'  # Default assumption

        Rf = medida.Rf

        # Simplified classification based on friction ratio
        if Rf < 1.0:
            return 'areia'  # Clean sands
        elif Rf < 2.0:
            return 'areia_siltosa'  # Silty sands
        elif Rf < 3.5:
            return 'silte_arenoso'  # Sandy silts
        elif Rf < 5.0:
            return 'silte_argiloso'  # Clayey silts
        else:
            return 'argila'  # Clays

    def obter_k(self, tipo_solo: str) -> float:
        """Get correlation factor k for soil type."""
        tipo_norm = tipo_solo.lower().replace(' ', '_')

        if 'argila' in tipo_norm:
            return self._correlacao.k_argila
        elif 'silte' in tipo_norm:
            return self._correlacao.k_silte
        elif 'pedregulho' in tipo_norm:
            return self._correlacao.k_pedregulho
        else:
            return self._correlacao.k_areia

    def converter_qc_para_nspt(
        self,
        qc: float,
        tipo_solo: str,
    ) -> int:
        """
        Convert qc (MPa) to equivalent N_SPT.

        N_SPT = qc (kPa) / k
        """
        k = self.obter_k(tipo_solo)
        qc_kpa = qc * 1000
        n_spt = qc_kpa / k
        return max(1, round(n_spt))

    def convert(
        self,
        perfil_cpt: PerfilCPT,
        intervalo: float = 1.0,
        nome_sondagem: str | None = None,
    ):
        """
        Convert CPT profile to equivalent SPT profile.

        Args:
            perfil_cpt: Source CPT profile.
            intervalo: Output SPT sampling interval in meters.
            nome_sondagem: Name for output profile.

        Returns:
            PerfilSPT with equivalent N_SPT values.
        """
        from calculus_core.domain.model import PerfilSPT

        nome = nome_sondagem or f'{perfil_cpt.nome_sondagem}_SPT'
        perfil_spt = PerfilSPT(nome_sondagem=nome, intervalo_padrao=intervalo)

        # Sample at regular intervals
        prof = perfil_cpt.profundidade_minima
        while prof <= perfil_cpt.profundidade_maxima:
            # Average CPT values in interval
            medidas_intervalo = [
                m
                for m in perfil_cpt
                if (prof - intervalo / 2)
                <= m.profundidade
                <= (prof + intervalo / 2)
            ]

            if medidas_intervalo:
                # Average qc and Rf
                qc_medio = sum(m.qc for m in medidas_intervalo) / len(
                    medidas_intervalo
                )

                # Infer soil type from average
                medida_ref = medidas_intervalo[len(medidas_intervalo) // 2]
                tipo_solo = self.inferir_tipo_solo(medida_ref)

                # Convert to N_SPT
                n_spt = self.converter_qc_para_nspt(qc_medio, tipo_solo)

                perfil_spt.adicionar_medida(prof, n_spt, tipo_solo)

            prof = round(prof + intervalo, 3)

        return perfil_spt


# =============================================================================
# CONVERSION REGISTRY
# =============================================================================


class ConversionRegistry:
    """
    Registry for profile conversion strategies.

    Allows registering and retrieving converters for specific
    source-target type pairs.
    """

    _converters: dict[tuple[SoilTestType, SoilTestType], type] = {}

    @classmethod
    def register(
        cls,
        source: SoilTestType,
        target: SoilTestType,
        converter_class: type,
    ) -> None:
        """Register a converter for a source-target pair."""
        cls._converters[(source, target)] = converter_class

    @classmethod
    def get_converter(
        cls,
        source: SoilTestType,
        target: SoilTestType,
    ) -> ProfileConverter | None:
        """Get converter for source-target pair."""
        converter_class = cls._converters.get((source, target))
        if converter_class:
            return converter_class()
        return None

    @classmethod
    def can_convert(cls, source: SoilTestType, target: SoilTestType) -> bool:
        """Check if conversion is available."""
        return (source, target) in cls._converters

    @classmethod
    def list_conversions(cls) -> list[tuple[str, str]]:
        """List all available conversions."""
        return [(s.value, t.value) for s, t in cls._converters.keys()]


# Register built-in converters
ConversionRegistry.register(
    SoilTestType.CPT, SoilTestType.SPT, CPTtoSPTConverter
)
ConversionRegistry.register(
    SoilTestType.CPTU, SoilTestType.SPT, CPTtoSPTConverter
)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def converter_cpt_para_spt(
    perfil_cpt: PerfilCPT,
    correlacao: str = 'robertson_1983',
    intervalo: float = 1.0,
):
    """
    Convenience function to convert CPT to equivalent SPT.

    Args:
        perfil_cpt: Source CPT profile.
        correlacao: Correlation name ('robertson_1983', 'aoki_velloso_1975', 'decourt_1995').
        intervalo: Output sampling interval.

    Returns:
        PerfilSPT with equivalent N_SPT values.

    Example:
        perfil_spt = converter_cpt_para_spt(perfil_cpt, 'robertson_1983')
        resultado = calculator.calcular(perfil_spt, estaca)
    """
    converter = CPTtoSPTConverter(nome_correlacao=correlacao)
    return converter.convert(perfil_cpt, intervalo=intervalo)


def listar_correlacoes_cpt_spt() -> list[str]:
    """List available CPT to SPT correlations."""
    return list(CATALOGOS_CORRELACAO_CPT_SPT.keys())


def obter_info_correlacao(nome: str) -> dict:
    """Get information about a CPT-SPT correlation."""
    if nome not in CATALOGOS_CORRELACAO_CPT_SPT:
        raise ValueError(f'Correlação não encontrada: {nome}')

    corr = CATALOGOS_CORRELACAO_CPT_SPT[nome]
    return {
        'nome': corr.nome,
        'k_argila': corr.k_argila,
        'k_silte': corr.k_silte,
        'k_areia': corr.k_areia,
        'k_pedregulho': corr.k_pedregulho,
        'referencia': corr.referencia,
    }
