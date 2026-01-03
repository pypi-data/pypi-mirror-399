"""
Décourt-Quaresma Coefficient Provider

This module contains the coefficient data and provider for the
Décourt-Quaresma (1978) method with 1996 revisions.
"""

# =============================================================================
# COEFFICIENT DATA - Décourt-Quaresma (1978)
# =============================================================================

COEF_K_DECOURT_QUARESMA_1978 = {
    'argila': {'deslocamento': 120, 'escavada': 100},
    'silte_arenoso': {'deslocamento': 200, 'escavada': 170},
    'silte_argiloso': {'deslocamento': 200, 'escavada': 140},
    'areia': {'deslocamento': 400, 'escavada': 300},
}

COEF_ALFA_DECOURT_QUARESMA_1996 = {
    'argila': {
        'cravada': 1,
        'escavada': 0.85,
        'escavada_bentonita': 0.85,
        'hélice_contínua': 0.3,
        'raiz': 0.6,
        'injetada': 1,
    },
    'silte': {
        'cravada': 1,
        'escavada': 0.60,
        'escavada_bentonita': 0.60,
        'hélice_contínua': 0.3,
        'raiz': 0.6,
        'injetada': 1,
    },
    'areia': {
        'cravada': 1,
        'escavada': 0.5,
        'escavada_bentonita': 0.5,
        'hélice_contínua': 0.3,
        'raiz': 0.5,
        'injetada': 1,
    },
}

COEF_BETA_DECOURT_QUARESMA_1996 = {
    'argila': {
        'cravada': 1,
        'escavada': 0.8,
        'escavada_bentonita': 0.9,
        'hélice_contínua': 1,
        'raiz': 1.5,
        'injetada': 3,
    },
    'silte': {
        'cravada': 1,
        'escavada': 0.65,
        'escavada_bentonita': 0.75,
        'hélice_contínua': 1,
        'raiz': 1.5,
        'injetada': 3,
    },
    'areia': {
        'cravada': 1,
        'escavada': 0.5,
        'escavada_bentonita': 0.6,
        'hélice_contínua': 1,
        'raiz': 1.5,
        'injetada': 3,
    },
}


# =============================================================================
# PROVIDER CLASS
# =============================================================================


class DecourtQuaresma1978Provider:
    """
    Coefficient provider for Décourt-Quaresma (1978) method.

    Implements the DecourtCoefficientProvider protocol from the domain layer.
    """

    def __init__(
        self,
        coef_K: dict | None = None,
        coef_alfa: dict | None = None,
        coef_beta: dict | None = None,
    ):
        """
        Initialize the provider with coefficient data.

        Args:
            coef_K: K coefficients by soil and process. Defaults to 1978 data.
            coef_alfa: Alpha coefficients. Defaults to 1996 revision.
            coef_beta: Beta coefficients. Defaults to 1996 revision.
        """
        self._coef_K = coef_K or COEF_K_DECOURT_QUARESMA_1978
        self._coef_alfa = coef_alfa or COEF_ALFA_DECOURT_QUARESMA_1996
        self._coef_beta = coef_beta or COEF_BETA_DECOURT_QUARESMA_1996

    def get_k(self, tipo_solo: str, processo_construcao: str) -> float:
        """
        Get K coefficient for soil type and construction process.

        Args:
            tipo_solo: Normalized soil type (argila, silte_arenoso, silte_argiloso, areia).
            processo_construcao: Construction process (deslocamento, escavada).

        Returns:
            K coefficient in kPa.

        Raises:
            ValueError: If combination not found.
        """
        # Normalize process to match table keys
        processo = processo_construcao.lower()
        if processo in ['escavada', 'hélice_contínua', 'raiz', 'injetada']:
            processo = 'escavada'
        else:
            processo = 'deslocamento'

        if tipo_solo not in self._coef_K:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Décourt-Quaresma: {tipo_solo}'
            )

        if processo not in self._coef_K[tipo_solo]:
            raise ValueError(
                f'Processo de construção não suportado: {processo}'
            )

        return self._coef_K[tipo_solo][processo]

    def get_alpha(self, tipo_solo: str, tipo_estaca: str) -> float:
        """
        Get alpha coefficient for soil type and pile type.

        Args:
            tipo_solo: Normalized soil type (argila, silte, areia).
            tipo_estaca: Normalized pile type.

        Returns:
            Alpha coefficient.

        Raises:
            ValueError: If combination not found.
        """
        # Map silte variants to silte
        if tipo_solo.startswith('silte'):
            tipo_solo_grupo = 'silte'
        elif tipo_solo.startswith('argila'):
            tipo_solo_grupo = 'argila'
        elif tipo_solo.startswith('areia'):
            tipo_solo_grupo = 'areia'
        else:
            tipo_solo_grupo = tipo_solo

        if tipo_solo_grupo not in self._coef_alfa:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Décourt-Quaresma: {tipo_solo}'
            )

        if tipo_estaca not in self._coef_alfa[tipo_solo_grupo]:
            raise ValueError(f'Tipo de estaca não suportado: {tipo_estaca}')

        return self._coef_alfa[tipo_solo_grupo][tipo_estaca]

    def get_beta(self, tipo_solo: str, tipo_estaca: str) -> float:
        """
        Get beta coefficient for soil type and pile type.

        Args:
            tipo_solo: Normalized soil type (argila, silte, areia).
            tipo_estaca: Normalized pile type.

        Returns:
            Beta coefficient.

        Raises:
            ValueError: If combination not found.
        """
        # Map silte variants to silte
        if tipo_solo.startswith('silte'):
            tipo_solo_grupo = 'silte'
        elif tipo_solo.startswith('argila'):
            tipo_solo_grupo = 'argila'
        elif tipo_solo.startswith('areia'):
            tipo_solo_grupo = 'areia'
        else:
            tipo_solo_grupo = tipo_solo

        if tipo_solo_grupo not in self._coef_beta:
            raise ValueError(
                f'Tipo de solo não suportado pelo método '
                f'de Décourt-Quaresma: {tipo_solo}'
            )

        if tipo_estaca not in self._coef_beta[tipo_solo_grupo]:
            raise ValueError(f'Tipo de estaca não suportado: {tipo_estaca}')

        return self._coef_beta[tipo_solo_grupo][tipo_estaca]
