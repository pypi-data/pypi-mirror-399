"""
Teixeira Coefficient Provider

This module contains the coefficient data and provider for the
Teixeira (1996) method.
"""

# =============================================================================
# COEFFICIENT DATA - Teixeira (1996)
# =============================================================================

COEFICIENTES_ALPHA_TEIXEIRA_1996 = {
    'argila_siltosa': {
        'pré_moldada': 110,
        'metálica': 110,
        'franki': 100,
        'escavada': 100,
        'raiz': 100,
    },
    'silte_argiloso': {
        'pré_moldada': 160,
        'metálica': 160,
        'franki': 120,
        'escavada': 110,
        'raiz': 110,
    },
    'argila_arenosa': {
        'pré_moldada': 210,
        'metálica': 210,
        'franki': 160,
        'escavada': 130,
        'raiz': 140,
    },
    'silte_arenoso': {
        'pré_moldada': 260,
        'metálica': 260,
        'franki': 210,
        'escavada': 160,
        'raiz': 160,
    },
    'areia_argilosa': {
        'pré_moldada': 300,
        'metálica': 300,
        'franki': 240,
        'escavada': 200,
        'raiz': 190,
    },
    'areia_siltosa': {
        'pré_moldada': 360,
        'metálica': 360,
        'franki': 300,
        'escavada': 240,
        'raiz': 220,
    },
    'areia': {
        'pré_moldada': 400,
        'metálica': 400,
        'franki': 340,
        'escavada': 270,
        'raiz': 260,
    },
    'areia_com_pedregulhos': {
        'pré_moldada': 440,
        'metálica': 440,
        'franki': 380,
        'escavada': 310,
        'raiz': 290,
    },
}

COEFICIENTES_BETA_TEIXEIRA_1996 = {
    'pré_moldada': 4,
    'metálica': 4,
    'franki': 5,
    'escavada': 4,
    'raiz': 6,
}


# =============================================================================
# PROVIDER CLASS
# =============================================================================


class Teixeira1996Provider:
    """
    Coefficient provider for Teixeira (1996) method.

    Implements the TeixeiraCoefficientProvider protocol from the domain layer.
    """

    def __init__(
        self,
        coef_alpha: dict | None = None,
        coef_beta: dict | None = None,
    ):
        """
        Initialize the provider with coefficient data.

        Args:
            coef_alpha: Alpha coefficients. Defaults to 1996 data.
            coef_beta: Beta coefficients. Defaults to 1996 data.
        """
        self._coef_alpha = coef_alpha or COEFICIENTES_ALPHA_TEIXEIRA_1996
        self._coef_beta = coef_beta or COEFICIENTES_BETA_TEIXEIRA_1996

    def get_alpha(self, tipo_solo: str, tipo_estaca: str) -> float:
        """
        Get alpha coefficient for soil type and pile type.

        Args:
            tipo_solo: Normalized soil type.
            tipo_estaca: Normalized pile type.

        Returns:
            Alpha coefficient.

        Raises:
            ValueError: If combination not found.
        """
        if tipo_solo not in self._coef_alpha:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Teixeira: {tipo_solo}'
            )

        if tipo_estaca not in self._coef_alpha[tipo_solo]:
            raise ValueError(
                f'Tipo de estaca não suportado pelo método '
                f'de Teixeira: {tipo_estaca}'
            )

        return self._coef_alpha[tipo_solo][tipo_estaca]

    def get_beta(self, tipo_estaca: str) -> float:
        """
        Get beta coefficient for pile type.

        Args:
            tipo_estaca: Normalized pile type.

        Returns:
            Beta coefficient.

        Raises:
            ValueError: If pile type not found.
        """
        if tipo_estaca not in self._coef_beta:
            raise ValueError(f'Tipo de estaca inválido: {tipo_estaca}')

        return self._coef_beta[tipo_estaca]
