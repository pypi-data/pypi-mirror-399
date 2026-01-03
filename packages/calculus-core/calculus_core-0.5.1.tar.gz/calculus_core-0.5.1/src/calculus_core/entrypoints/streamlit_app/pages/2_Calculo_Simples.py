"""
Página: Cálculo Simples
"""

import altair as alt
import pandas as pd
import streamlit as st

from calculus_core.bootstrap import get_all_calculators
from calculus_core.domain.pile_types import EstacaFactory
from calculus_core.service_layer import CalculationRequest, CalculationService

# =============================================================================
# SETUP
# =============================================================================

st.set_page_config(page_title='Cálculo Simples', page_icon='🧮', layout='wide')

if not st.session_state.get('perfil_spt'):
    st.warning(
        '⚠️ Perfil de solo não definido. Vá para a página **Dados do Solo**.'
    )
    st.stop()

# =============================================================================
# UI
# =============================================================================

st.title('🧮 Cálculo de Capacidade de Carga')
st.caption('Analise uma solução específica detalhadamente.')

coluna_configuracao, coluna_resultados = st.columns([1, 2])

with coluna_configuracao:
    st.subheader('Configuração')

    with st.container(border=True):
        # Pile Type Selection
        tipos_disponiveis = EstacaFactory.listar_tipos_estaca()
        tipo_selecionado = st.selectbox(
            'Tipo de Fundação', tipos_disponiveis, index=0
        )

        # Profile Selection
        perfis_disponiveis = EstacaFactory.listar_perfis_por_tipo(
            tipo_selecionado
        )
        perfil_selecionado = st.selectbox(
            'Perfil Comercial', perfis_disponiveis
        )

        # Helper Info
        try:
            info = EstacaFactory.obter_info_perfil(
                tipo_selecionado, perfil_selecionado
            )
            d = info.get('dimensao_principal_m', 0)
            if d == 0:
                d = info.get('diametro_m', 0)
            st.caption(f'📏 Dimensão: {d * 100:.0f} cm')
        except Exception:
            pass

        st.markdown('---')

        # Method Selection
        metodos = list(get_all_calculators().keys())
        metodos_selecionados = st.multiselect(
            'Métodos de Cálculo', metodos, default=[metodos[0]]
        )

    botao_calcular = st.button(
        'Calcular Curva', type='primary', width='stretch'
    )

with coluna_resultados:
    if botao_calcular and metodos_selecionados:
        st.subheader('Resultados')

        results_data = []

        try:
            # Create a reference pile (prototype)
            estaca_ref = EstacaFactory.criar_de_catalogo(
                tipo_selecionado, perfil_selecionado, cota_assentamento=1
            )

            request = CalculationRequest(
                perfil_spt=st.session_state.perfil_spt,
                tipo_estaca=estaca_ref.tipo,
                processo_construcao=estaca_ref.processo_construcao,
                formato=estaca_ref.formato,
                secao_transversal=estaca_ref.secao_transversal,
                cota_assentamento=None,  # Calculate all depths
                estaca_prototype=estaca_ref,  # Use prototype for catalog piles
            )

            for metodo in metodos_selecionados:
                calc = get_all_calculators()[metodo]
                service = CalculationService(calc)

                # Execute calculation using the service
                result = service.calculate_all_depths(request)

                if result.success:
                    for r in result.resultados:
                        r_dict = r.to_dict()
                        r_dict['Método'] = metodo
                        results_data.append(r_dict)
                else:
                    st.error(f'Erro no método {metodo}: {result.error}')

            df_res = pd.DataFrame(results_data)

            if not df_res.empty:
                # Chart
                chart = (
                    alt.Chart(df_res)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            'capacidade_carga_adm',
                            title='Carga Admissível (kN)',
                        ),
                        y=alt.Y(
                            'cota',
                            title='Profundidade (m)',
                            scale=alt.Scale(reverse=True),
                        ),
                        color='Método',
                        tooltip=[
                            'cota',
                            'capacidade_carga_adm',
                            'resistencia_ponta',
                            'resistencia_lateral',
                        ],
                    )
                    .interactive()
                    .properties(height=500)
                )

                st.altair_chart(chart, width='stretch')

                # Clean Table
                st.dataframe(
                    df_res[
                        [
                            'cota',
                            'Método',
                            'capacidade_carga_adm',
                            'resistencia_ponta',
                            'resistencia_lateral',
                        ]
                    ].sort_values(['cota', 'Método']),
                    height=300,
                    width='stretch',
                )
            else:
                st.info('Nenhum resultado gerado.')

        except Exception as e:
            st.error(f'Erro no cálculo: {e}')
