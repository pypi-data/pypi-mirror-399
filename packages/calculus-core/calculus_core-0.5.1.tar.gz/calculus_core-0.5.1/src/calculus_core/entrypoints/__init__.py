"""
Entrypoints Layer - External Interfaces

This package contains the entry points for external consumers:
- CLI: Command-line interface
- Streamlit App: Web-based user interface
- (Future) API: REST API endpoints

Entrypoints should:
- Handle user input/output
- Convert external data to domain objects
- Call services for business operations
- NOT contain business logic
"""

from .cli import run_app

__all__ = ['run_app']
