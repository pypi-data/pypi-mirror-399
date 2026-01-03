"""
Calculus-Core Web Interface - Home
"""

import pandas as pd
import streamlit as st

from calculus_core.domain.model import PerfilSPT
from calculus_core.entrypoints.streamlit_app.constants import (
    EXEMPLO_SPT,
    SOLOS_MAP_INIT,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title='Calculus-Core',
    page_icon='🏗️',
    layout='wide',
)

# =============================================================================
# GLOBAL STATE INITIALIZATION
# =============================================================================


def create_default_profile() -> PerfilSPT:
    """Create the default soil profile instance."""
    perfil = PerfilSPT(nome_sondagem='Exemplo Inicial')
    medidas = []
    for layer in EXEMPLO_SPT:
        solo_id = SOLOS_MAP_INIT.get(layer['solo'], 'br_solo_residual_geral')
        medidas.append((float(layer['prof']), int(layer['n_spt']), solo_id))
    perfil.adicionar_medidas(medidas)
    return perfil


if 'perfil_spt' not in st.session_state:
    st.session_state.perfil_spt = create_default_profile()

if 'perfil_cpt' not in st.session_state:
    st.session_state.perfil_cpt = None

if 'spt_data_inicial' not in st.session_state:
    st.session_state.spt_data_inicial = pd.DataFrame(EXEMPLO_SPT)


# =============================================================================
# HOME PAGE CONTENT
# =============================================================================

st.title('🏗️ Calculus-Core')

st.markdown("""
### Bem-vindo ao Sistema de Cálculo de Fundações

Esta aplicação utiliza a biblioteca `calculus-core` para realizar dimensionamento e análise de capacidade de carga de estacas usando métodos semi-empíricos brasileiros.

#### 🚀 Funcionalidades

*   **📍 Dados do Solo**: Gerencie perfis de sondagem SPT ou importe dados.
*   **🧮 Cálculo Simples**: Dimensione uma estaca específica e analise sua curva de carga.
*   **🚀 Comparativo em Lote**: Compare múltiplos métodos ou tipos de fundação simultaneamente.


#### 📚 Métodos Disponíveis
*   Aoki-Velloso (1975)
*   Décourt-Quaresma (1978)
*   Teixeira (1996)
*   Aoki-Velloso-Laprovitera (1988)

---
*Navegue pelas páginas usando o menu lateral.*
""")

if st.session_state.perfil_spt is None:
    st.info(
        '💡 Dica: Comece acessando a página **Dados do Solo** para definir o perfil de sondagem.'
    )
else:
    st.success(
        f'✅ Perfil de solo ativo: {len(st.session_state.perfil_spt)} camadas carregadas.'
    )
