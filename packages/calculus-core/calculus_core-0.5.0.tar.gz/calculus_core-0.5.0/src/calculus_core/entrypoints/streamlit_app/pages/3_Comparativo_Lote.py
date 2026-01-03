"""
Página: Comparativo em Lote
"""

import altair as alt
import pandas as pd
import streamlit as st

from calculus_core.domain.method_registry import CalculationMethodRegistry
from calculus_core.domain.pile_types import EstacaFactory
from calculus_core.service_layer import (
    calcular_todos_metodos_todas_estacas,
    calcular_todos_metodos_uma_estaca,
    calcular_um_metodo_todas_estacas,
    serializar_resultados,
)

# =============================================================================
# SETUP
# =============================================================================

st.set_page_config(
    page_title='Comparativo em Lote', page_icon='🚀', layout='wide'
)

if not st.session_state.get('perfil_spt'):
    st.warning(
        '⚠️ Perfil de solo não definido. Vá para a página **Dados do Solo**.'
    )
    st.stop()

# Helper: Max Depth and Ideal Default
MAX_DEPTH = float(st.session_state.perfil_spt.profundidade_maxima)
medidas_profile = st.session_state.perfil_spt.medidas
if len(medidas_profile) >= 2:
    IDEAL_DEFAULT = float(medidas_profile[-2].profundidade)
else:
    IDEAL_DEFAULT = MAX_DEPTH

# =============================================================================
# HELPER: ID MAPPING
# =============================================================================

# Map Display Name -> ID
METHODS_INFO = CalculationMethodRegistry.list_all()
NAME_TO_ID = {m.name: m.id for m in METHODS_INFO}
ID_TO_NAME = {m.id: m.name for m in METHODS_INFO}


# =============================================================================
# UI
# =============================================================================

st.title('🚀 Comparativo em Lote')
st.caption('Compare múltiplos cenários para tomada de decisão.')

tab1, tab2, tab3 = st.tabs(
    [
        '📊 Comparar Métodos',
        '🏗️ Comparar Estacas',
        '🌍 Comparativo Global',
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: MÉTODOS (Mesma Estaca)
# -----------------------------------------------------------------------------
with tab1:
    st.subheader('Análise de Dispersão de Métodos')
    st.markdown('Verifique como diferentes autores avaliam a mesma fundação.')

    coluna_configuracao, coluna_resultados = st.columns([1, 2])

    with coluna_configuracao:
        with st.container(border=True):
            tipos = EstacaFactory.listar_tipos_estaca()
            tipo_estaca_selecionada = st.selectbox(
                'Tipo de Estaca', tipos, key='batch_t'
            )
            perfil_estaca_selecionado = st.selectbox(
                'Perfil Comercial',
                EstacaFactory.listar_perfis_por_tipo(tipo_estaca_selecionada),
                key='batch_p',
            )
            cota = st.number_input(
                'Cota de Assentamento (m)',
                min_value=0.0,
                max_value=MAX_DEPTH,
                step=0.1,
                value=IDEAL_DEFAULT,
                format='%.2f',
                key='batch_c',
            )

            run_methods = st.button(
                'Executar Comparação', type='primary', width='stretch'
            )

    with coluna_resultados:
        if run_methods:
            with st.spinner('Calculando...'):
                estaca = EstacaFactory.criar_de_catalogo(
                    tipo_estaca_selecionada, perfil_estaca_selecionado, cota
                )
                resultados = calcular_todos_metodos_uma_estaca(
                    st.session_state.perfil_spt, estaca
                )

                dados = serializar_resultados(resultados)
                df = pd.DataFrame(dados)

                # Add Human Readable Name
                df['metodo_nome'] = df['metodo'].map(ID_TO_NAME)

                # Split success vs error
                df_ok = df.dropna(subset=['capacidade_carga_adm'])
                df_error = df[df['capacidade_carga_adm'].isna()]

                if not df_ok.empty:
                    base = alt.Chart(df_ok).encode(
                        y=alt.Y('metodo_nome', title=None)
                    )

                    bar = base.mark_bar().encode(
                        x=alt.X('capacidade_carga_adm', title='Qadm (kN)'),
                        color=alt.Color('metodo_nome', legend=None),
                        tooltip=['metodo_nome', 'capacidade_carga_adm'],
                    )

                    text = base.mark_text(align='left', dx=2).encode(
                        x='capacidade_carga_adm',
                        text=alt.Text('capacidade_carga_adm', format='.0f'),
                    )

                    st.altair_chart(bar + text, width='stretch')

                    # Metrics
                    st.metric(
                        'Média Qadm',
                        f'{df_ok["capacidade_carga_adm"].mean():.0f} kN',
                    )

                if not df_error.empty:
                    with st.expander('⚠️ Métodos não aplicáveis ou com erro'):
                        st.dataframe(
                            df_error[['metodo_nome', 'erro']],
                            width='stretch',
                        )


# -----------------------------------------------------------------------------
# TAB 2: ESTACAS (Mesmo Método)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader('Estudo de Viabilidade')
    st.markdown('Encontre a solução mais eficiente para uma carga alvo.')

    coluna_configuracao, coluna_resultados = st.columns([1, 2])

    with coluna_configuracao:
        with st.container(border=True):
            # Select by NAME, retrieve ID
            metodo_nome = st.selectbox(
                'Método de Referência', list(NAME_TO_ID.keys())
            )
            metodo_id = NAME_TO_ID[metodo_nome]

            diametro_referencia = st.number_input(
                'Diâmetro de Referência (m)',
                0.2,
                1.5,
                0.4,
                0.05,
                help='O sistema buscará em cada catálogo o perfil mais próximo deste diâmetro.',
            )
            cota_viabilidade = st.number_input(
                'Cota (m)',
                min_value=0.0,
                max_value=MAX_DEPTH,
                step=0.1,
                value=IDEAL_DEFAULT,
                format='%.2f',
                key='viab_c',
            )

            run_piles = st.button(
                'Comparar Soluções', type='primary', width='stretch'
            )

    with coluna_resultados:
        if run_piles:
            with st.spinner('Analisando todos os catálogos...'):
                try:
                    resultados = calcular_um_metodo_todas_estacas(
                        st.session_state.perfil_spt,
                        metodo_id,  # Pass ID, not name
                        cota_viabilidade,
                        diametro_referencia=diametro_referencia,
                    )

                    dados = serializar_resultados(resultados)
                    df = pd.DataFrame(dados)
                    df = df.dropna(subset=['capacidade_carga_adm'])

                    if not df.empty:
                        # Chart
                        chart = (
                            alt.Chart(df)
                            .mark_bar()
                            .encode(
                                x=alt.X(
                                    'estaca',
                                    sort='-y',
                                    title='Solução (Tipo e Perfil)',
                                ),
                                y=alt.Y(
                                    'capacidade_carga_adm', title='Qadm (kN)'
                                ),
                                color=alt.value('#4C78A8'),
                                tooltip=[
                                    'estaca',
                                    'capacidade_carga_adm',
                                    'resistencia_ponta',
                                    'resistencia_lateral',
                                ],
                            )
                            .interactive()
                        )

                        st.altair_chart(chart, width='stretch')

                        st.dataframe(
                            df[
                                [
                                    'estaca',
                                    'capacidade_carga_adm',
                                    'resistencia_ponta',
                                    'resistencia_lateral',
                                ]
                            ].sort_values(
                                'capacidade_carga_adm', ascending=False
                            ),
                            width='stretch',
                        )
                    else:
                        st.warning('Nenhum resultado válido encontrado.')

                except Exception as e:
                    st.error(f'Erro na análise: {e}')


# -----------------------------------------------------------------------------
# TAB 3: GLOBAL (Matriz Completa)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader('Matriz de Decisão Global')
    st.markdown(
        'Cruze todos os métodos com todos os tipos de estaca para uma visão macro.'
    )

    coluna_configuracao, coluna_resultados = st.columns([1, 2])

    with coluna_configuracao:
        with st.container(border=True):
            diametro_global = st.number_input(
                'Diâmetro Aprox. (m)', 0.2, 1.5, 0.4, 0.1, key='glob_d'
            )
            cota_global = st.number_input(
                'Cota (m)',
                min_value=0.0,
                max_value=MAX_DEPTH,
                step=0.1,
                value=IDEAL_DEFAULT,
                format='%.2f',
                key='glob_c',
            )

            run_global = st.button(
                'Gerar Matriz Global', type='primary', width='stretch'
            )

    with coluna_resultados:
        if run_global:
            with st.spinner('Processando matriz complexa...'):
                resultados = calcular_todos_metodos_todas_estacas(
                    st.session_state.perfil_spt,
                    cota_global,
                    diametro_referencia=diametro_global,
                )

                dados = serializar_resultados(resultados)
                df = pd.DataFrame(dados)
                df['metodo_nome'] = df['metodo'].map(ID_TO_NAME)

                df_ok = df.dropna(subset=['capacidade_carga_adm'])

                if not df_ok.empty:
                    # Heatmap
                    chart = (
                        alt.Chart(df_ok)
                        .mark_rect()
                        .encode(
                            x=alt.X('estaca', title='Estaca'),
                            y=alt.Y('metodo_nome', title='Método'),
                            color=alt.Color(
                                'capacidade_carga_adm',
                                title='Qadm (kN)',
                                scale=alt.Scale(scheme='viridis'),
                            ),
                            tooltip=[
                                'estaca',
                                'metodo_nome',
                                'capacidade_carga_adm',
                            ],
                        )
                        .properties(height=400)
                    )

                    st.altair_chart(chart, width='stretch')

                    # Pivot Table view
                    pivot = df_ok.pivot_table(
                        index='estaca',
                        columns='metodo_nome',
                        values='capacidade_carga_adm',
                    )
                    st.dataframe(
                        pivot.style.format('{:.0f}').background_gradient(
                            cmap='viridis', axis=None
                        ),
                        width='stretch',
                    )

                else:
                    st.error('Nenhum resultado válido gerado.')
