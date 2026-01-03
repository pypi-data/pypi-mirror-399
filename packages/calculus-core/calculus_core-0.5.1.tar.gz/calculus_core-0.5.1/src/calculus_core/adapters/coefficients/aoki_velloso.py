"""
Aoki-Velloso Coefficient Providers

This module contains the coefficient data and providers for the
Aoki-Velloso (1975) method and its revision by Laprovitera (1988).
"""


# =============================================================================
# COEFFICIENT DATA - Aoki-Velloso (1975)
# =============================================================================

COEFICIENTES_AOKI_VELLOSO_1975 = {
    'areia': {'k_kpa': 1000, 'alpha_perc': 1.4},
    'areia_siltosa': {'k_kpa': 800, 'alpha_perc': 2.0},
    'areia_silto_argilosa': {'k_kpa': 700, 'alpha_perc': 2.4},
    'areia_argilosa': {'k_kpa': 600, 'alpha_perc': 3.0},
    'areia_argilo_siltosa': {'k_kpa': 500, 'alpha_perc': 2.8},
    'silte': {'k_kpa': 400, 'alpha_perc': 3.0},
    'silte_arenoso': {'k_kpa': 550, 'alpha_perc': 2.2},
    'silte_areno_argiloso': {'k_kpa': 450, 'alpha_perc': 2.8},
    'silte_argiloso': {'k_kpa': 230, 'alpha_perc': 3.4},
    'silte_argilo_arenoso': {'k_kpa': 250, 'alpha_perc': 3.0},
    'argila': {'k_kpa': 200, 'alpha_perc': 6.0},
    'argila_arenosa': {'k_kpa': 350, 'alpha_perc': 2.4},
    'argila_areno_siltosa': {'k_kpa': 300, 'alpha_perc': 2.8},
    'argila_siltosa': {'k_kpa': 220, 'alpha_perc': 4.0},
    'argila_silto_arenosa': {'k_kpa': 330, 'alpha_perc': 3.0},
}

FATORES_F1_F2_AOKI_VELLOSO_1975 = {
    'franki': {'F1': 2.50, 'F2': lambda f1: 2 * f1},
    'metálica': {'F1': 1.75, 'F2': lambda f1: 2 * f1},
    'pré_moldada': {
        'F1': lambda D: 1 + (D / 0.8),
        'F2': lambda f1: 2 * f1,
    },
    'escavada': {'F1': 3.00, 'F2': lambda f1: 2 * f1},
    'raiz': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'hélice_contínua': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'ômega': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
}

# =============================================================================
# COEFFICIENT DATA - Aoki-Velloso (1975) revised by Laprovitera (1988)
# =============================================================================

COEFICIENTES_AOKI_VELLOSO_LAPROVITERA_1988 = {
    'areia': {
        'k_kpa': 600,
        'alpha_perc': 1.4,
        'alpha_star_perc': 1.4,
    },
    'areia_siltosa': {
        'k_kpa': 530,
        'alpha_perc': 1.9,
        'alpha_star_perc': 1.9,
    },
    'areia_silto_argilosa': {
        'k_kpa': 530,
        'alpha_perc': 2.4,
        'alpha_star_perc': 2.4,
    },
    'areia_argilo_siltosa': {
        'k_kpa': 530,
        'alpha_perc': 2.8,
        'alpha_star_perc': 2.8,
    },
    'areia_argilosa': {
        'k_kpa': 530,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_arenoso': {
        'k_kpa': 480,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_areno_argiloso': {
        'k_kpa': 380,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte': {
        'k_kpa': 480,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_argilo_arenoso': {
        'k_kpa': 380,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_argiloso': {
        'k_kpa': 300,
        'alpha_perc': 3.4,
        'alpha_star_perc': 3.4,
    },
    'argila_arenosa': {
        'k_kpa': 480,
        'alpha_perc': 4.0,
        'alpha_star_perc': 2.6,
    },
    'argila_areno_siltosa': {
        'k_kpa': 380,
        'alpha_perc': 4.5,
        'alpha_star_perc': 3.0,
    },
    'argila_silto_arenosa': {
        'k_kpa': 380,
        'alpha_perc': 5.0,
        'alpha_star_perc': 3.3,
    },
    'argila_siltosa': {
        'k_kpa': 250,
        'alpha_perc': 5.5,
        'alpha_star_perc': 3.6,
    },
    'argila': {
        'k_kpa': 250,
        'alpha_perc': 6.0,
        'alpha_star_perc': 4.0,
    },
}

FATORES_F1_F2_AOKI_VELLOSO_LAPROVITERA_1988 = {
    'franki': {'F1': 2.50, 'F2': 3.0},
    'metálica': {'F1': 2.4, 'F2': 3.4},
    'pré_moldada': {'F1': 2.0, 'F2': 3.5},
    'escavada': {'F1': 4.50, 'F2': 4.50},
    'raiz': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'hélice_contínua': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'ômega': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
}


# =============================================================================
# PROVIDER CLASSES
# =============================================================================


class AokiVelloso1975Provider:
    """
    Coefficient provider for Aoki-Velloso (1975) method.

    Implements the CoefficientProvider protocol from the domain layer.
    """

    def __init__(
        self,
        coeficientes: dict | None = None,
        fatores: dict | None = None,
    ):
        """
        Initialize the provider with coefficient data.

        Args:
            coeficientes: Soil coefficients (K, alpha). Defaults to 1975 data.
            fatores: F1/F2 factors. Defaults to 1975 data.
        """
        self._coeficientes = coeficientes or COEFICIENTES_AOKI_VELLOSO_1975
        self._fatores = fatores or FATORES_F1_F2_AOKI_VELLOSO_1975

    def get_k(self, tipo_solo: str) -> float:
        """
        Get K coefficient for a soil type.

        Args:
            tipo_solo: Normalized soil type.

        Returns:
            K coefficient in kPa.

        Raises:
            ValueError: If soil type not found.
        """
        if tipo_solo not in self._coeficientes:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Aoki e Velloso: {tipo_solo}'
            )
        return self._coeficientes[tipo_solo]['k_kpa']

    def get_alpha(self, tipo_solo: str, confiavel: bool = True) -> float:
        """
        Get alpha coefficient for a soil type.

        Args:
            tipo_solo: Normalized soil type.
            confiavel: Whether the SPT profile is reliable.

        Returns:
            Alpha coefficient as a decimal (not percentage).

        Raises:
            ValueError: If soil type not found.
        """
        if tipo_solo not in self._coeficientes:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Aoki e Velloso: {tipo_solo}'
            )

        coef = self._coeficientes[tipo_solo]

        # Use alpha_star if available and profile is unreliable
        if not confiavel and 'alpha_star_perc' in coef:
            return coef['alpha_star_perc'] / 100

        return coef['alpha_perc'] / 100

    def get_f1_f2(
        self, tipo_estaca: str, diametro: float | None = None
    ) -> tuple[float, float]:
        """
        Get F1 and F2 factors for a pile type.

        Args:
            tipo_estaca: Normalized pile type.
            diametro: Pile diameter (required for some pile types).

        Returns:
            Tuple of (F1, F2).

        Raises:
            ValueError: If pile type not found or diameter required but not provided.
        """
        if tipo_estaca not in self._fatores:
            raise ValueError(
                f'Tipo de estaca não suportado pelo método '
                f'de Aoki e Velloso: {tipo_estaca}'
            )

        dados = self._fatores[tipo_estaca]
        valor_f1 = dados['F1']
        func_f2 = dados['F2']

        # Calculate F1 (may be a function of diameter)
        if callable(valor_f1):
            if diametro is None:
                raise ValueError(
                    f'Diâmetro da estaca é necessário para calcular '
                    f'F1 para estaca {tipo_estaca}.'
                )
            f1 = valor_f1(diametro)
        else:
            f1 = valor_f1

        # Calculate F2 (may be a function of F1)
        if callable(func_f2):
            f2 = func_f2(f1)
        else:
            f2 = func_f2

        return f1, f2


class AokiVellosoLaprovitera1988Provider(AokiVelloso1975Provider):
    """
    Coefficient provider for Aoki-Velloso (1975) revised by Laprovitera (1988).

    Uses the revised coefficient tables with alpha_star values.
    """

    def __init__(self):
        """Initialize with Laprovitera's revised coefficients."""
        super().__init__(
            coeficientes=COEFICIENTES_AOKI_VELLOSO_LAPROVITERA_1988,
            fatores=FATORES_F1_F2_AOKI_VELLOSO_LAPROVITERA_1988,
        )
