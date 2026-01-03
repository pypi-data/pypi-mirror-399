"""
Adapters Layer - Infrastructure Concerns

This package contains adapters that connect the domain to external
infrastructure like databases, file systems, and external services.

Key Components:
- repository: Data access abstractions and implementations
- coefficients: Coefficient data providers for calculation methods
"""

from .coefficients import (
    AokiVelloso1975Provider,
    AokiVellosoLaprovitera1988Provider,
    DecourtQuaresma1978Provider,
    Teixeira1996Provider,
)

__all__ = [
    'AokiVelloso1975Provider',
    'AokiVellosoLaprovitera1988Provider',
    'DecourtQuaresma1978Provider',
    'Teixeira1996Provider',
]
