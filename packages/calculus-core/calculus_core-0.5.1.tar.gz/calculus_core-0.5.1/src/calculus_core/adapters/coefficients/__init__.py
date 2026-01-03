"""
Coefficient Providers Package

This package contains coefficient data providers for different calculation
methods. These providers implement the protocols defined in the domain layer,
enabling dependency injection.
"""

from .aoki_velloso import (
    AokiVelloso1975Provider,
    AokiVellosoLaprovitera1988Provider,
)
from .decourt_quaresma import DecourtQuaresma1978Provider
from .teixeira import Teixeira1996Provider

__all__ = [
    'AokiVelloso1975Provider',
    'AokiVellosoLaprovitera1988Provider',
    'DecourtQuaresma1978Provider',
    'Teixeira1996Provider',
]
