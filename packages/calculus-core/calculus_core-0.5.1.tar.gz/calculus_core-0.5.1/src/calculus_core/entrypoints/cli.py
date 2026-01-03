"""
CLI Entry Point

Command-line interface for the calculus-core package.
Launches the Streamlit web application.
"""

import os
import sys


def run_app():
    """Launch the Streamlit web application."""
    try:
        import streamlit.web.cli as stcli
    except ImportError:
        print('Erro: Dependências do Streamlit não encontradas.')
        print(
            'Para usar a interface web, instale o pacote com a opção [streamlit]:'
        )
        print('    pip install calculus-core[streamlit]')
        print('    ou')
        print('    uv add calculus-core[streamlit]')
        sys.exit(1)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(app_dir, 'streamlit_app', 'app.py')

    if not os.path.exists(app_path):
        print(f'Erro: Arquivo da aplicação não encontrado em {app_path}')
        sys.exit(1)

    sys.argv = ['streamlit', 'run', app_path]
    sys.exit(stcli.main())


if __name__ == '__main__':
    run_app()
