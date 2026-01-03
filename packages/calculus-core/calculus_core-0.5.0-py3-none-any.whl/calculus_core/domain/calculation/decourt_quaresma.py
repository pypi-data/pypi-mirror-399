"""
Décourt-Quaresma Calculation Strategy

Pure domain logic for the Décourt-Quaresma (1978) method.
Coefficients are injected through the DecourtCoefficientProvider protocol.
"""

from calculus_core.domain.calculation.base import (
    DecourtCoefficientProvider,
    MetodoCalculo,
)
from calculus_core.domain.model import Estaca, PerfilSPT
from calculus_core.domain.value_objects import ResultadoCalculo

# Mapping for soil type normalization
MAPEAMENTO_SOLO_DECOURT = {
    'argila': [
        'argila',
        'argila_arenosa',
        'argila_areno_siltosa',
        'argila_siltosa',
        'argila_silto_arenosa',
    ],
    'silte': [
        'silte',
        'silte_arenoso',
        'silte_areno_argiloso',
        'silte_argiloso',
        'silte_argilo_arenoso',
    ],
    'areia': [
        'areia',
        'areia_com_pedregulhos',
        'areia_siltosa',
        'areia_silto_argilosa',
        'areia_argilosa',
        'areia_argilo_siltosa',
    ],
}


def normalizar_tipo_solo_decourt(tipo_solo: str, para_K: bool = False) -> str:
    """
    Normalize soil type for Décourt-Quaresma method.

    Args:
        tipo_solo: Original soil type.
        para_K: If True and soil is 'silte', return 'silte_arenoso'.

    Returns:
        Normalized soil type (argila, silte, or areia).
    """
    norm = tipo_solo.lower().replace(' ', '_').replace('-', '_')

    # Special case for K coefficient lookup
    if para_K and norm == 'silte':
        return 'silte_arenoso'

    # Map to group
    for grupo, solos in MAPEAMENTO_SOLO_DECOURT.items():
        if norm in solos:
            return grupo

    return norm


def normalizar_tipo_estaca_decourt(tipo_estaca: str) -> str:
    """
    Normalize pile type for Décourt-Quaresma method.

    Args:
        tipo_estaca: Original pile type.

    Returns:
        Normalized pile type.
    """
    norm = tipo_estaca.lower().replace(' ', '_').replace('-', '_')

    # Map displacement piles to 'cravada'
    cravadas = ['cravada', 'franki', 'pré_moldada', 'metálica', 'ômega']
    if norm in cravadas:
        return 'cravada'

    # Keep other types as-is
    return norm


class DecourtQuaresmaCalculator(MetodoCalculo):
    """
    Calculator for the Décourt-Quaresma (1978) method.

    This method uses average N_SPT values around the tip (Np) and
    along the shaft (Nl) with alpha and beta correction factors.
    """

    def __init__(self, coefficient_provider: DecourtCoefficientProvider):
        """
        Initialize with a coefficient provider.

        Args:
            coefficient_provider: Provider for K, alpha, beta coefficients.
        """
        self._provider = coefficient_provider

    def calcular_np(
        self, perfil_spt: PerfilSPT, cota_assentamento: int
    ) -> float:
        """
        Calculate average N_SPT at the tip (mean of layer above and below).

        Args:
            perfil_spt: SPT profile.
            cota_assentamento: Settlement depth.

        Returns:
            Average Np value.
        """
        cota_acima = cota_assentamento
        cota_abaixo = cota_assentamento + 1

        # Use interpolation or valid lookup strategy instead of strict check
        # This supports fractional depths not exactly matching layers
        try:
            medida_acima = perfil_spt.obter_medida(
                cota_acima, estrategia='interpolar'
            )
        except ValueError:
            # Fallback if too shallow/deep (though interpolar usually handles bounds)
            raise ValueError(f'Cota {cota_acima} fora dos limites do perfil.')

        try:
            medida_abaixo = perfil_spt.obter_medida(
                cota_abaixo, estrategia='interpolar'
            )
            return (medida_acima.N_SPT + medida_abaixo.N_SPT) / 2
        except ValueError:
            # Last layer logic
            return (medida_acima.N_SPT + 50) / 2

    def calcular_nl(self, perfil_spt: PerfilSPT, estaca: Estaca) -> float:
        """
        Calculate average N_SPT along the shaft (excluding tip region).

        Args:
            perfil_spt: SPT profile.
            estaca: Pile characteristics.

        Returns:
            Average Nl value.
        """
        cota_tip = estaca.cota_assentamento

        # Filter layers strictly above the tip (shaft only)
        # N_p usually involves the tip and the layer below.
        # N_l is the average along the shaft.
        # We include all layers up to but not including the tip depth.
        # Assuming measurements are ordered by depth.
        N_spts = [
            m.N_SPT for m in perfil_spt.medidas if m.profundidade < cota_tip
        ]

        if not N_spts:
            return 0.0

        return sum(N_spts) / len(N_spts)

    @staticmethod
    def calcular_rp(
        alpha: float, Np: float, K: float, area_ponta: float
    ) -> float:
        """
        Calculate tip resistance.

        Rp = α * Np * K * Ap

        Args:
            alpha: Alpha factor for pile/soil combination.
            Np: Average N_SPT at tip.
            K: K coefficient (kPa).
            area_ponta: Tip area (m²).

        Returns:
            Tip resistance in kN.
        """
        return alpha * Np * K * area_ponta

    @staticmethod
    def calcular_rl(
        beta: float,
        Nl: float,
        perimetro: float,
        comprimento: float,
    ) -> float:
        """
        Calculate lateral resistance.

        Rl = β * (Nl/3 + 1) * U * L * 10

        Args:
            beta: Beta factor for pile/soil combination.
            Nl: Average N_SPT along shaft.
            perimetro: Pile perimeter (m).
            comprimento: Embedded length (m).

        Returns:
            Lateral resistance in kN.
        """
        # Décourt-Quaresma formula: fl = 10 * (Nl/3 + 1) kPa
        fl = 10.0 * (Nl / 3.0 + 1.0)
        return beta * fl * perimetro * comprimento

    def calcular(
        self, perfil_spt: PerfilSPT, estaca: Estaca
    ) -> ResultadoCalculo:
        """
        Execute the Décourt-Quaresma calculation.

        Args:
            perfil_spt: SPT profile.
            estaca: Pile characteristics.

        Returns:
            ResultadoCalculo with complete results.
        """
        cota = estaca.cota_assentamento

        # Get soil type at tip for coefficients
        if cota + 1 in perfil_spt:
            camada_ponta = perfil_spt.obter_medida(cota + 1)
        else:
            camada_ponta = perfil_spt.obter_medida(cota)

        tipo_solo_ponta = normalizar_tipo_solo_decourt(camada_ponta.tipo_solo)
        tipo_solo_K = normalizar_tipo_solo_decourt(
            camada_ponta.tipo_solo, para_K=True
        )
        tipo_estaca = normalizar_tipo_estaca_decourt(estaca.tipo)

        # Calculate Np and Nl
        Np = self.calcular_np(perfil_spt, cota)
        Nl = self.calcular_nl(perfil_spt, estaca)

        # Get coefficients
        K = self._provider.get_k(tipo_solo_K, estaca.processo_construcao)
        alpha = self._provider.get_alpha(tipo_solo_ponta, tipo_estaca)
        beta = self._provider.get_beta(tipo_solo_ponta, tipo_estaca)

        # Calculate resistances
        Rp = self.calcular_rp(alpha, Np, K, estaca.area_ponta)

        # Lateral resistance uses shaft length (cota - 1)
        comprimento_fuste = estaca.cota_assentamento - 1
        Rl = self.calcular_rl(
            beta, Nl, estaca.perimetro, max(comprimento_fuste, 0)
        )

        # Calculate allowable load
        capacidade_carga = Rp + Rl
        carga_adm = self.calcular_carga_adm_decourt(Rp, Rl)

        return ResultadoCalculo(
            cota=cota,
            resistencia_ponta=Rp,
            resistencia_lateral=Rl,
            capacidade_carga=capacidade_carga,
            capacidade_carga_adm=carga_adm,
        )

    @staticmethod
    def calcular_carga_adm_decourt(Rp: float, Rl: float) -> float:
        """
        Calculate allowable load using Décourt-Quaresma formula.

        Q_adm = Rp/4 + Rl/1.3

        Args:
            Rp: Tip resistance.
            Rl: Lateral resistance.

        Returns:
            Allowable load capacity.
        """
        return Rp / 4.0 + Rl / 1.3

    def cota_parada(self, perfil_spt: PerfilSPT) -> int:
        """
        Determine stopping depth for Décourt-Quaresma.

        Returns the second-to-last layer depth.

        Args:
            perfil_spt: SPT profile.

        Returns:
            Maximum calculation depth.
        """
        return len(perfil_spt) - 1
