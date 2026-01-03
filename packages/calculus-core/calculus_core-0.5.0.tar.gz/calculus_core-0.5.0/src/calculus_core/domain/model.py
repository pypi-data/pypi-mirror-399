"""
Domain Model - Core Entities

This module contains the core domain entities for foundation load capacity
calculations. These entities encapsulate business rules and behaviors.

Entities:
- MedidaSPT: Single SPT measurement at a specific depth
- PerfilSPT: Complete SPT profile with multiple measurements
- Estaca: Foundation pile with geometric properties
"""

import math
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from typing import Iterator, Literal

# =============================================================================
# CONSTANTS
# =============================================================================

NSPT_IMPENETRAVEL = 50
PROFUNDIDADE_TOLERANCIA = 0.001  # 1mm precision


# =============================================================================
# SPT MEASUREMENT
# =============================================================================


@dataclass
class MedidaSPT:
    """
    Value object representing a single SPT measurement.

    Attributes:
        profundidade: Depth in meters (supports fractional values).
        N_SPT: SPT blow count (number of blows for 30cm penetration).
        tipo_solo: Soil type classification.
        espessura_camada: Optional layer thickness in meters.
    """

    profundidade: float
    N_SPT: int
    tipo_solo: str
    espessura_camada: float | None = None

    def __post_init__(self):
        if self.profundidade < 0:
            raise ValueError('Profundidade não pode ser negativa.')
        if self.N_SPT < 0:
            raise ValueError('N_SPT não pode ser negativo.')
        self.profundidade = round(self.profundidade, 3)

    def __repr__(self) -> str:
        return (
            f'MedidaSPT(prof={self.profundidade}m, '
            f'N={self.N_SPT}, solo={self.tipo_solo!r})'
        )

    @property
    def is_impenetravel(self) -> bool:
        """Check if this measurement indicates impenetrable soil."""
        return (
            self.tipo_solo.lower() == 'impenetravel'
            or self.N_SPT >= NSPT_IMPENETRAVEL
        )


# =============================================================================
# SPT PROFILE
# =============================================================================


class PerfilSPT:
    """
    Aggregate representing a complete SPT (Standard Penetration Test) profile.

    Contains a collection of measurements and provides domain behavior for
    accessing them with various lookup strategies.

    Attributes:
        nome_sondagem: Boring identification name.
        confiavel: Whether the SPT data is considered reliable.
        intervalo_padrao: Standard test interval in meters.

    Example:
        perfil = PerfilSPT(nome_sondagem='SP-01')
        perfil.adicionar_medidas([
            (1.0, 5, 'argila'),
            (1.5, 7, 'argila_arenosa'),
            (2.0, 10, 'areia'),
        ])
        medida = perfil.obter_medida(1.5)
    """

    def __init__(
        self,
        nome_sondagem: str = 'SP-01',
        confiavel: bool = True,
        intervalo_padrao: float = 1.0,
    ):
        self.nome_sondagem = nome_sondagem
        self.confiavel = confiavel
        self.intervalo_padrao = intervalo_padrao
        self._medidas: list[MedidaSPT] = []
        self._profundidades_cache: list[float] = []

    @property
    def medidas(self) -> list[MedidaSPT]:
        """Return a copy of the measurements list."""
        return list(self._medidas)

    def _rebuild_cache(self) -> None:
        """Rebuild the depth lookup cache."""
        self._profundidades_cache = [m.profundidade for m in self._medidas]

    def adicionar_medida(
        self,
        profundidade: float,
        N_SPT: int,
        tipo_solo: str,
        espessura_camada: float | None = None,
    ) -> None:
        """
        Add a single SPT measurement.

        Args:
            profundidade: Depth in meters.
            N_SPT: SPT blow count.
            tipo_solo: Soil type.
            espessura_camada: Optional layer thickness.
        """
        medida = MedidaSPT(profundidade, N_SPT, tipo_solo, espessura_camada)
        self._medidas.append(medida)
        self._medidas.sort(key=lambda x: x.profundidade)
        self._rebuild_cache()

    def adicionar_medidas(
        self,
        dados: list[tuple[float, int, str]]
        | list[tuple[float, int, str, float]],
    ) -> None:
        """
        Add multiple SPT measurements at once.

        Args:
            dados: List of tuples (profundidade, N_SPT, tipo_solo)
                   or (profundidade, N_SPT, tipo_solo, espessura_camada).
        """
        for item in dados:
            if len(item) == 3:
                prof, n, solo = item
                espessura = None
            else:
                prof, n, solo, espessura = item

            medida = MedidaSPT(prof, n, solo, espessura)
            self._medidas.append(medida)

        self._medidas.sort(key=lambda x: x.profundidade)
        self._rebuild_cache()

    def obter_medida(
        self,
        profundidade: float,
        estrategia: Literal[
            'exata', 'mais_proxima', 'anterior', 'interpolar'
        ] = 'mais_proxima',
    ) -> MedidaSPT:
        """
        Get the SPT measurement at a specific depth.

        Args:
            profundidade: Depth in meters.
            estrategia: Lookup strategy:
                - 'exata': Exact match only, raises error if not found.
                - 'mais_proxima': Return the closest measurement (default).
                - 'anterior': Return measurement at or before this depth.
                - 'interpolar': Linearly interpolate N_SPT between layers.

        Returns:
            The MedidaSPT at or near the specified depth.

        Raises:
            ValueError: If no measurement found with 'exata' strategy.
        """
        if not self._medidas:
            raise ValueError('Nenhuma medida registrada no perfil SPT.')

        profundidade = round(profundidade, 3)

        # Beyond last measurement: return impenetrable
        if profundidade > self._medidas[-1].profundidade:
            delta = profundidade - self._medidas[-1].profundidade
            if delta <= self.intervalo_padrao:
                return MedidaSPT(
                    profundidade, NSPT_IMPENETRAVEL, 'impenetravel'
                )
            raise ValueError(
                f'Profundidade {profundidade}m está muito abaixo da '
                f'máxima registrada ({self._medidas[-1].profundidade}m).'
            )

        # Exact match
        for medida in self._medidas:
            if (
                abs(medida.profundidade - profundidade)
                < PROFUNDIDADE_TOLERANCIA
            ):
                return medida

        if estrategia == 'exata':
            raise ValueError(
                f'Medida não encontrada para profundidade {profundidade}m.'
            )

        if estrategia == 'mais_proxima':
            return min(
                self._medidas,
                key=lambda x: abs(x.profundidade - profundidade),
            )

        if estrategia == 'anterior':
            idx = bisect_right(self._profundidades_cache, profundidade) - 1
            if idx < 0:
                return self._medidas[0]
            return self._medidas[idx]

        if estrategia == 'interpolar':
            return self._interpolar(profundidade)

        raise ValueError(f'Estratégia desconhecida: {estrategia}')

    def _interpolar(self, profundidade: float) -> MedidaSPT:
        """Interpolate N_SPT linearly between adjacent measurements."""
        if profundidade <= self._medidas[0].profundidade:
            return self._medidas[0]

        if profundidade >= self._medidas[-1].profundidade:
            return self._medidas[-1]

        idx_sup = bisect_left(self._profundidades_cache, profundidade)
        idx_inf = idx_sup - 1

        if idx_inf < 0:
            return self._medidas[0]

        m_inf = self._medidas[idx_inf]
        m_sup = self._medidas[idx_sup]

        delta_prof = m_sup.profundidade - m_inf.profundidade
        if delta_prof == 0:
            return m_inf

        fator = (profundidade - m_inf.profundidade) / delta_prof
        n_interpolado = round(
            m_inf.N_SPT + fator * (m_sup.N_SPT - m_inf.N_SPT)
        )

        return MedidaSPT(
            profundidade=profundidade,
            N_SPT=n_interpolado,
            tipo_solo=m_inf.tipo_solo,
        )

    def obter_camada(self, profundidade: float) -> MedidaSPT:
        """Get the soil layer that contains a specific depth."""
        return self.obter_medida(profundidade, estrategia='anterior')

    def obter_n_spt_intervalo(
        self,
        prof_inicio: float,
        prof_fim: float,
        metodo: Literal['media', 'minimo', 'maximo'] = 'media',
    ) -> float:
        """
        Get aggregate N_SPT for a depth interval.

        Args:
            prof_inicio: Start depth in meters.
            prof_fim: End depth in meters.
            metodo: Aggregation method ('media', 'minimo', 'maximo').

        Returns:
            Aggregate N_SPT value for the interval.
        """
        if prof_inicio > prof_fim:
            prof_inicio, prof_fim = prof_fim, prof_inicio

        medidas_intervalo = [
            m
            for m in self._medidas
            if prof_inicio <= m.profundidade <= prof_fim
        ]

        if not medidas_intervalo:
            m_inicio = self.obter_medida(prof_inicio, 'interpolar')
            m_fim = self.obter_medida(prof_fim, 'interpolar')
            medidas_intervalo = [m_inicio, m_fim]

        valores = [m.N_SPT for m in medidas_intervalo]

        if metodo == 'media':
            return sum(valores) / len(valores)
        elif metodo == 'minimo':
            return min(valores)
        elif metodo == 'maximo':
            return max(valores)

        return sum(valores) / len(valores)

    def iterar_profundidades(
        self,
        inicio: float | None = None,
        fim: float | None = None,
        passo: float | None = None,
    ) -> Iterator[tuple[float, MedidaSPT]]:
        """
        Iterate over depths with associated measurements.

        Args:
            inicio: Start depth (default: first measurement).
            fim: End depth (default: last measurement).
            passo: Step size (default: intervalo_padrao).

        Yields:
            Tuples of (depth, measurement) for each step.
        """
        if not self._medidas:
            return

        if inicio is None:
            inicio = self._medidas[0].profundidade
        if fim is None:
            fim = self._medidas[-1].profundidade
        if passo is None:
            passo = self.intervalo_padrao

        prof_atual = inicio
        while prof_atual <= fim + PROFUNDIDADE_TOLERANCIA:
            medida = self.obter_medida(prof_atual, 'mais_proxima')
            yield (prof_atual, medida)
            prof_atual = round(prof_atual + passo, 3)

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

    def profundidades_disponiveis(self) -> list[float]:
        """Return all depths with measurements."""
        return list(self._profundidades_cache)

    def __repr__(self) -> str:
        if self._medidas:
            return (
                f'PerfilSPT(nome={self.nome_sondagem!r}, '
                f'medidas={len(self._medidas)}, '
                f'prof=[{self.profundidade_minima:.1f}-'
                f'{self.profundidade_maxima:.1f}m])'
            )
        return f'PerfilSPT(nome={self.nome_sondagem!r}, medidas=0)'

    def __len__(self) -> int:
        return len(self._medidas)

    def __getitem__(self, index: int) -> MedidaSPT:
        return self._medidas[index]

    def __iter__(self):
        return iter(self._medidas)

    def __contains__(self, profundidade: float) -> bool:
        """Check if a specific depth has a measurement."""
        return any(
            abs(m.profundidade - profundidade) < PROFUNDIDADE_TOLERANCIA
            for m in self._medidas
        )


# =============================================================================
# ESTACA (PILE)
# =============================================================================


@dataclass
class Estaca:
    """
    Entity representing a foundation pile.

    Attributes:
        tipo: Pile type (e.g., 'pré_moldada', 'escavada', 'hélice_contínua').
        processo_construcao: Construction process ('deslocamento', 'escavada').
        formato: Cross-section shape ('circular' or 'quadrada').
        secao_transversal: Diameter (circular) or side length (square) in meters.
        cota_assentamento: Installation depth in meters.
    """

    tipo: str
    processo_construcao: str
    formato: str
    secao_transversal: float
    cota_assentamento: float

    def __post_init__(self):
        if self.secao_transversal <= 0:
            raise ValueError('Seção transversal deve ser positiva.')
        if self.cota_assentamento < 0.5:
            raise ValueError('Cota de assentamento deve ser >= 0.5m.')

        if self.formato not in ('circular', 'quadrada'):
            raise ValueError("O formato deve ser 'circular' ou 'quadrada'.")

        self.cota_assentamento = round(self.cota_assentamento, 2)

    @property
    def diametro(self) -> float:
        """Return the diameter (circular) or side length (square)."""
        return self.secao_transversal

    @property
    def area_ponta(self) -> float:
        """Calculate the tip area in m²."""
        if self.formato == 'circular':
            raio = self.secao_transversal / 2
            return math.pi * (raio**2)
        elif self.formato == 'quadrada':
            return self.secao_transversal**2
        # Generic fallback or allow manual injection in future
        # For now, assume square-like usage if unknown
        return self.secao_transversal**2

    @property
    def perimetro(self) -> float:
        """Calculate the perimeter in meters."""
        if self.formato == 'circular':
            return math.pi * self.secao_transversal
        elif self.formato == 'quadrada':
            return 4 * self.secao_transversal
        # Generic fallback
        return 4 * self.secao_transversal

    def comprimento_embutido(self) -> float:
        """Return the embedded length of the pile."""
        return self.cota_assentamento

    def na_cota(self, nova_cota: float) -> 'Estaca':
        """Create a copy of this pile at a new depth."""
        return Estaca(
            tipo=self.tipo,
            processo_construcao=self.processo_construcao,
            formato=self.formato,
            secao_transversal=self.secao_transversal,
            cota_assentamento=nova_cota,
        )
