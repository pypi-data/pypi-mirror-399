"""
Aoki-Velloso Calculation Strategy

Pure domain logic for the Aoki-Velloso (1975) method.
Coefficients are injected through the CoefficientProvider protocol.
"""

from calculus_core.domain.calculation.base import (
    CoefficientProvider,
    MetodoCalculo,
)
from calculus_core.domain.model import Estaca, PerfilSPT
from calculus_core.domain.value_objects import ResultadoCalculo


def normalizar_tipo_solo(tipo_solo: str) -> str:
    """Normalize soil type string."""
    norm = tipo_solo.lower().replace(' ', '_').replace('-', '_')
    # Map sand with gravel to sand
    if norm == 'areia_com_pedregulhos':
        return 'areia'
    return norm


def normalizar_tipo_estaca(tipo_estaca: str) -> str:
    """Normalize pile type string."""
    return tipo_estaca.lower().replace(' ', '_').replace('-', '_')


class AokiVellosoCalculator(MetodoCalculo):
    """
    Calculator for the Aoki-Velloso (1975) method.

    This implementation follows the Single Responsibility Principle:
    - Pure calculation logic only
    - Coefficient data injected via provider
    """

    def __init__(self, coefficient_provider: CoefficientProvider):
        """
        Initialize with a coefficient provider.

        Args:
            coefficient_provider: Provider for K, alpha, F1, F2 coefficients.
        """
        self._provider = coefficient_provider

    def calcular_np(
        self, perfil_spt: PerfilSPT, cota_assentamento: float
    ) -> int:
        """
        Find N_SPT at the pile tip support layer.

        The tip support layer is 1 meter below the settlement depth.

        Args:
            perfil_spt: SPT profile.
            cota_assentamento: Settlement depth.

        Returns:
            N_SPT value at the tip support layer.

        Raises:
            ValueError: If depths are invalid.
        """
        if cota_assentamento not in perfil_spt:
            raise ValueError(
                'Cota de assentamento inválida para o perfil SPT.'
            )

        cota_apoio_ponta = cota_assentamento + 1
        if cota_apoio_ponta not in perfil_spt:
            raise ValueError(
                'Cota de apoio da ponta inválida para o perfil SPT.'
            )

        return perfil_spt.obter_medida(cota_apoio_ponta).N_SPT

    @staticmethod
    def calcular_rp(K: float, Np: int, f1: float, area_ponta: float) -> float:
        """
        Calculate tip resistance.

        Args:
            K: Soil K coefficient (kPa).
            Np: N_SPT at tip.
            f1: F1 factor for pile type.
            area_ponta: Tip area (m²).

        Returns:
            Tip resistance in kN.
        """
        return (K * Np) / f1 * area_ponta

    @staticmethod
    def calcular_rl_parcial(
        alpha: float,
        K: float,
        Nl: int,
        f2: float,
        perimetro: float,
        espessura_camada: float = 1.0,
    ) -> float:
        """
        Calculate partial lateral resistance for a single layer.

        Args:
            alpha: Alpha coefficient for soil type.
            K: K coefficient for soil type (kPa).
            Nl: N_SPT at the layer.
            f2: F2 factor for pile type.
            perimetro: Pile perimeter (m).
            espessura_camada: Layer thickness (m).

        Returns:
            Partial lateral resistance in kN.
        """
        return perimetro * espessura_camada * (alpha * K * Nl) / f2

    def calcular(
        self, perfil_spt: PerfilSPT, estaca: Estaca
    ) -> ResultadoCalculo:
        """
        Execute the Aoki-Velloso calculation.

        Args:
            perfil_spt: SPT profile.
            estaca: Pile characteristics.

        Returns:
            ResultadoCalculo with complete results.
        """
        cota = estaca.cota_assentamento

        # Get Np at tip (1m below settlement)
        cota_ponta = cota + 1
        medida_ponta = perfil_spt.obter_medida(
            cota_ponta, estrategia='mais_proxima'
        )
        Np = medida_ponta.N_SPT

        # Get coefficients for tip
        tipo_solo_norm = normalizar_tipo_solo(medida_ponta.tipo_solo)
        tipo_estaca_norm = normalizar_tipo_estaca(estaca.tipo)

        K = self._provider.get_k(tipo_solo_norm)
        f1, f2 = self._provider.get_f1_f2(
            tipo_estaca_norm, estaca.secao_transversal
        )

        # Calculate tip resistance
        Rp = self.calcular_rp(K, Np, f1, estaca.area_ponta)

        # Calculate lateral resistance using actual layers
        Rl = 0.0

        # Filter layers along the shaft (strictly above tip)
        layers = [m for m in perfil_spt.medidas if m.profundidade < cota]

        for camada in layers:
            tipo_solo_camada = normalizar_tipo_solo(camada.tipo_solo)

            K_layer = self._provider.get_k(tipo_solo_camada)
            alpha = self._provider.get_alpha(
                tipo_solo_camada, perfil_spt.confiavel
            )

            # Determine layer thickness
            # Use explicit thickness if available, otherwise default interval
            dz = camada.espessura_camada
            if dz is None:
                dz = perfil_spt.intervalo_padrao

            Rl += self.calcular_rl_parcial(
                alpha=alpha,
                K=K_layer,
                Nl=camada.N_SPT,
                f2=f2,
                perimetro=estaca.perimetro,
                espessura_camada=dz,
            )

        # Calculate allowable load
        capacidade_carga = Rp + Rl
        carga_adm = self.calcular_carga_admissivel(Rp, Rl)

        return ResultadoCalculo(
            cota=cota,
            resistencia_ponta=Rp,
            resistencia_lateral=Rl,
            capacidade_carga=capacidade_carga,
            capacidade_carga_adm=carga_adm,
        )

    def cota_parada(self, perfil_spt: PerfilSPT) -> int:
        """
        Determine stopping depth for Aoki-Velloso.

        Returns the last layer (maximum depth) of the SPT profile.

        Args:
            perfil_spt: SPT profile.

        Returns:
            Maximum calculation depth.
        """
        return len(perfil_spt) - 1
