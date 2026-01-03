"""
Teixeira Calculation Strategy

Pure domain logic for the Teixeira (1996) method.
Coefficients are injected through the TeixeiraCoefficientProvider protocol.
"""

from calculus_core.domain.calculation.base import (
    MetodoCalculo,
    TeixeiraCoefficientProvider,
)
from calculus_core.domain.model import Estaca, PerfilSPT
from calculus_core.domain.value_objects import ResultadoCalculo

# Mapping for soil type normalization
MAPEAMENTO_SOLO_TEIXEIRA = {
    'argila_siltosa': ['argila_siltosa', 'argila_silto_arenosa'],
    'silte_argiloso': ['silte_argiloso', 'silte_argilo_arenoso'],
    'argila_arenosa': ['argila_arenosa', 'argila_areno_siltosa'],
    'silte_arenoso': ['silte_arenoso', 'silte_areno_argiloso'],
    'areia_argilosa': ['areia_argilosa', 'areia_argilo_siltosa'],
    'areia_siltosa': ['areia_siltosa', 'areia_silto_argilosa'],
}


def normalizar_tipo_solo_teixeira(tipo_solo: str) -> str:
    """
    Normalize soil type for Teixeira method.

    Args:
        tipo_solo: Original soil type.

    Returns:
        Normalized soil type.
    """
    norm = tipo_solo.lower().replace(' ', '_').replace('-', '_')

    for grupo, solos in MAPEAMENTO_SOLO_TEIXEIRA.items():
        if norm in solos:
            return grupo

    return norm


def normalizar_tipo_estaca_teixeira(tipo_estaca: str) -> str:
    """
    Normalize pile type for Teixeira method.

    Args:
        tipo_estaca: Original pile type.

    Returns:
        Normalized pile type.
    """
    return tipo_estaca.lower().replace(' ', '_').replace('-', '_')


class TeixeiraCalculator(MetodoCalculo):
    """
    Calculator for the Teixeira (1996) method.

    This method uses a specific interval for Np calculation based on
    pile diameter and simple formulas for resistance.
    """

    def __init__(self, coefficient_provider: TeixeiraCoefficientProvider):
        """
        Initialize with a coefficient provider.

        Args:
            coefficient_provider: Provider for alpha and beta coefficients.
        """
        self._provider = coefficient_provider

    def calcular_np(
        self,
        perfil_spt: PerfilSPT,
        cota_assentamento: float,
        diametro: float,
    ) -> float:
        """
        Calculate average N_SPT at tip using Teixeira's interval.

        Interval: [cota - 4*D, cota + 1*D]

        Args:
            perfil_spt: SPT profile.
            cota_assentamento: Settlement depth.
            diametro: Pile diameter (m).

        Returns:
            Average Np value.
        """
        intervalo_inicio = cota_assentamento - 4 * diametro
        intervalo_fim = cota_assentamento + 1 * diametro

        return perfil_spt.obter_n_spt_intervalo(
            intervalo_inicio, intervalo_fim, metodo='media'
        )

    def calcular_nl(
        self, perfil_spt: PerfilSPT, cota_assentamento: float
    ) -> float:
        """
        Calculate average N_SPT along the shaft.

        Args:
            perfil_spt: SPT profile.
            cota_assentamento: Settlement depth.

        Returns:
            Average Nl value.
        """
        prof_inicio = perfil_spt.profundidade_minima
        return perfil_spt.obter_n_spt_intervalo(
            prof_inicio, cota_assentamento, metodo='media'
        )

    @staticmethod
    def calcular_rp(alpha: float, Np: float, area_ponta: float) -> float:
        """
        Calculate tip resistance.

        Rp = α * Np * Ap

        Args:
            alpha: Alpha coefficient for soil/pile combination.
            Np: Average N_SPT at tip.
            area_ponta: Tip area (m²).

        Returns:
            Tip resistance in kN.
        """
        return alpha * Np * area_ponta

    @staticmethod
    def calcular_rl(
        beta: float,
        Nl: float,
        perimetro: float,
        comprimento: float,
    ) -> float:
        """
        Calculate lateral resistance.

        Rl = β * Nl * U * L

        Args:
            beta: Beta coefficient for pile type.
            Nl: Average N_SPT along shaft.
            perimetro: Pile perimeter (m).
            comprimento: Embedded length (m).

        Returns:
            Lateral resistance in kN.
        """
        return beta * Nl * perimetro * comprimento

    def calcular(
        self, perfil_spt: PerfilSPT, estaca: Estaca
    ) -> ResultadoCalculo:
        """
        Execute the Teixeira calculation.

        Args:
            perfil_spt: SPT profile.
            estaca: Pile characteristics.

        Returns:
            ResultadoCalculo with complete results.
        """
        cota = estaca.cota_assentamento

        # Get soil type at tip for alpha coefficient
        if cota + 1 in perfil_spt:
            camada_ponta = perfil_spt.obter_medida(cota + 1)
        else:
            camada_ponta = perfil_spt.obter_medida(cota)

        tipo_solo = normalizar_tipo_solo_teixeira(camada_ponta.tipo_solo)
        tipo_estaca = normalizar_tipo_estaca_teixeira(estaca.tipo)

        # Calculate Np and Nl
        Np = self.calcular_np(perfil_spt, cota, estaca.secao_transversal)
        Nl = self.calcular_nl(perfil_spt, cota)

        # Get coefficients
        alpha = self._provider.get_alpha(tipo_solo, tipo_estaca)
        beta = self._provider.get_beta(tipo_estaca)

        # Calculate resistances
        Rp = self.calcular_rp(alpha, Np, estaca.area_ponta)

        # Lateral resistance uses shaft length (cota - 1)
        comprimento_fuste = cota - 1
        Rl = self.calcular_rl(
            beta, Nl, estaca.perimetro, max(comprimento_fuste, 0)
        )

        # Calculate allowable load (minimum of two methods)
        capacidade_carga = Rp + Rl
        carga_adm = self.calcular_carga_adm_teixeira(Rp, Rl)

        return ResultadoCalculo(
            cota=cota,
            resistencia_ponta=Rp,
            resistencia_lateral=Rl,
            capacidade_carga=capacidade_carga,
            capacidade_carga_adm=carga_adm,
        )

    @staticmethod
    def calcular_carga_adm_teixeira(Rp: float, Rl: float) -> float:
        """
        Calculate allowable load using Teixeira's method.

        Uses the minimum of:
        - NBR method: (Rp + Rl) / 2
        - Décourt-Quaresma method: Rp/4 + Rl/1.5

        Args:
            Rp: Tip resistance.
            Rl: Lateral resistance.

        Returns:
            Allowable load capacity.
        """
        nbr_qadm = (Rp + Rl) / 2.0
        decourt_qadm = Rp / 4.0 + Rl / 1.5
        return min(nbr_qadm, decourt_qadm)

    def cota_parada(self, perfil_spt: PerfilSPT) -> int:
        """
        Determine stopping depth for Teixeira.

        Returns the second-to-last layer depth.

        Args:
            perfil_spt: SPT profile.

        Returns:
            Maximum calculation depth.
        """
        return len(perfil_spt) - 1
