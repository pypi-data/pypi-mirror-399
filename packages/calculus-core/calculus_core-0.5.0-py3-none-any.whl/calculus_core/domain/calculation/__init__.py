"""
Calculation Domain - Strategy Pattern Implementations

This package contains the calculation strategies for different foundation
load capacity methods. Each method is implemented as a strategy that can
be injected with coefficient data.
"""

from .aoki_velloso import AokiVellosoCalculator
from .base import CoefficientProvider, MetodoCalculo
from .decourt_quaresma import DecourtQuaresmaCalculator
from .teixeira import TeixeiraCalculator

__all__ = [
    'CoefficientProvider',
    'MetodoCalculo',
    'AokiVellosoCalculator',
    'DecourtQuaresmaCalculator',
    'TeixeiraCalculator',
]
