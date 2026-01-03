"""
Página: Dados do Solo
Gerenciamento de Perfis SPT
"""

import altair as alt
import pandas as pd
import streamlit as st

from calculus_core.domain.model import PerfilSPT
from calculus_core.entrypoints.streamlit_app.constants import (
    EXEMPLO_SPT,
    SOLOS_VALIDOS_MAP,
)

# =============================================================================
# SETUP
# =============================================================================

st.set_page_config(page_title='Dados do Solo', page_icon='📍', layout='wide')

if 'perfil_spt' not in st.session_state:
    st.session_state.perfil_spt = None

# =============================================================================
# CONSTANTS & DEFAULTS
# =============================================================================

# Imported from constants.py

# =============================================================================
# PAGE LAYOUT
# =============================================================================


st.title('📍 Dados do Solo')
st.caption('Defina o perfil geotécnico para os cálculos.')

tab_manual, tab_spt_csv, tab_cpt = st.tabs(
    ['Entrada Manual', 'Importar SPT (CSV)', 'Importar CPT (CSV)']
)

# =============================================================================
# TAB 1: ENTRADA MANUAL
# =============================================================================
with tab_manual:
    coluna_importacao, coluna_visualizacao = st.columns([1, 1], gap='large')

    with coluna_importacao:
        st.subheader('Editor Manual')

        # Load Initial Data
        if 'spt_data' not in st.session_state:
            if 'spt_data_inicial' in st.session_state:
                st.session_state.spt_data = st.session_state.spt_data_inicial
            else:
                # Fallback
                st.session_state.spt_data = pd.DataFrame(EXEMPLO_SPT)

        if st.button('🔄 Resetar para Exemplo Padrão'):
            st.session_state.spt_data = pd.DataFrame(EXEMPLO_SPT)

            # Update profile immediately
            try:
                perfil = PerfilSPT(nome_sondagem='Exemplo Padrão')
                medidas = []
                for _, row in st.session_state.spt_data.iterrows():
                    # Map solo string back to ID using the init map logic
                    solo_id = SOLOS_VALIDOS_MAP.get(
                        row['solo'], 'br_solo_residual_geral'
                    )
                    medidas.append(
                        (float(row['prof']), int(row['n_spt']), solo_id)
                    )

                perfil.adicionar_medidas(medidas)
                st.session_state.perfil_spt = perfil
                st.toast('Perfil resetado com sucesso!', icon='✅')

            except Exception as e:
                st.error(f'Erro ao regenerar perfil padrão: {e}')

            st.rerun()

        edited_df = st.data_editor(
            st.session_state.spt_data,
            column_config={
                'prof': st.column_config.NumberColumn(
                    'Profundidade (m)', min_value=0, step=0.5, format='%.1f'
                ),
                'n_spt': st.column_config.NumberColumn(
                    'N_SPT', min_value=0, step=1
                ),
                'solo': st.column_config.SelectboxColumn(
                    'Tipo de Solo',
                    options=list(SOLOS_VALIDOS_MAP.keys()),
                    required=True,
                ),
            },
            num_rows='dynamic',
            width='stretch',
            key='spt_editor',
        )

        # Create Profile Object
        if st.button(
            '✅ Validar e Processar Perfil (Manual)',
            type='primary',
            width='stretch',
        ):
            try:
                perfil = PerfilSPT(nome_sondagem='Sondagem Manual')
                medidas = []

                # Ordenar por profundidade
                df_sorted = edited_df.sort_values(by='prof')

                for _, row in df_sorted.iterrows():
                    # Get normalized identifier from map
                    solo_id = SOLOS_VALIDOS_MAP.get(row['solo'])
                    if not solo_id:
                        st.error(f'Tipo de solo inválido: {row["solo"]}')
                        st.stop()

                    medidas.append(
                        (float(row['prof']), int(row['n_spt']), solo_id)
                    )

                perfil.adicionar_medidas(medidas)
                st.session_state.perfil_spt = perfil
                st.toast('Perfil processado com sucesso!', icon='✅')
                st.session_state.spt_data = df_sorted  # Save sorted back

            except Exception as e:
                st.error(f'Erro ao processar perfil: {str(e)}')

    with coluna_visualizacao:
        # Shared visualization logic could be a function, but keeping inline for now to minimize diff complexity
        pass  # We'll render the viz at the bottom or duplicate it in tabs?
        # Strategy: Let's render the ACTIVE profile visualization at the very bottom of the page,
        # regardless of which tab is active, OR inside each tab.
        # Given the layout description, "Dados do Solo" usually shows the active profile.
        # Let's put the visualization in a shared area below tabs or inside each tab for confirmation.
        # The original code had side-by-side. Let's keep side-by-side for Manual.
        # For CSVs, we might want side-by-side too.

self_viz_manual = True


# =============================================================================
# SHARED VISUALIZATION HELPER
# =============================================================================
def render_active_profile_viz():
    st.subheader('Visualização do Perfil Ativo')

    if st.session_state.perfil_spt:
        # Visualization Logic
        data = []
        for m in st.session_state.perfil_spt._medidas:
            # FIX: m.tipo_solo is a string, not an object
            data.append(
                {
                    'Profundidade': m.profundidade,
                    'N_SPT': m.N_SPT,
                    'Tipo': m.tipo_solo,
                }
            )

        df_viz = pd.DataFrame(data)

        # Chart
        chart = (
            alt.Chart(df_viz)
            .mark_line(point=True)
            .encode(
                y=alt.Y(
                    'Profundidade',
                    scale=alt.Scale(reverse=True),
                    title='Profundidade (m)',
                ),
                x=alt.X('N_SPT', title='N_SPT (golpes/30cm)'),
                tooltip=['Profundidade', 'N_SPT', 'Tipo'],
                color=alt.value('#FF4B4B'),
            )
            .properties(height=500)
        )

        st.altair_chart(chart, width='stretch')

        # Info Box
        st.info(f"""
        **Resumo do Perfil Ativo:**
        - **Nome:** {st.session_state.perfil_spt.nome_sondagem}
        - **Prof. Máxima:** {st.session_state.perfil_spt.profundidade_maxima} m
        - **Camadas:** {len(st.session_state.perfil_spt)}
        """)

    else:
        st.warning(
            '⚠️ Nenhum perfil processado. Utilize uma das abas para carregar dados.'
        )


# Render viz for manual tab
with tab_manual:
    with coluna_visualizacao:
        render_active_profile_viz()


# =============================================================================
# TAB 2: IMPORTAR SPT (CSV)
# =============================================================================
with tab_spt_csv:
    col_upload, col_preview = st.columns([1, 1], gap='large')

    with col_upload:
        st.subheader('Carregar Arquivo SPT')

        st.markdown('**Formato esperado (exemplo):**')
        st.code(
            """prof,n_spt,solo
1.0,4,Argila Siltosa
2.0,8,Areia
...""",
            language='csv',
        )

        uploaded_spt = st.file_uploader(
            'Carregar arquivo CSV (SPT)',
            type='csv',
            key='spt_uploader',
            help='Colunas esperadas: prof, n_spt, solo (opcional)',
        )

        if uploaded_spt:
            df_spt_upload = pd.read_csv(uploaded_spt)
            st.dataframe(df_spt_upload.head(), height=150)

            with st.expander('Configuração de Colunas', expanded=True):
                c_prof = st.selectbox(
                    'Profundidade',
                    df_spt_upload.columns,
                    index=0,
                    key='spt_col_prof',
                )
                c_nspt = st.selectbox(
                    'N_SPT', df_spt_upload.columns, index=1, key='spt_col_nspt'
                )

                # Try to find 'solo' column or allow default
                default_solo_idx = (
                    2 if len(df_spt_upload.columns) > 2 else None
                )
                use_solo_col = st.checkbox(
                    'Ler tipo de solo do CSV?',
                    value=bool(default_solo_idx is not None),
                )

                c_solo = None
                default_soil_type = None

                if use_solo_col:
                    c_solo = st.selectbox(
                        'Tipo de Solo',
                        df_spt_upload.columns,
                        index=default_solo_idx or 0,
                        key='spt_col_solo',
                    )
                else:
                    default_soil_type = st.selectbox(
                        'Solo Padrão (para todas as camadas)',
                        list(SOLOS_VALIDOS_MAP.keys()),
                    )

            if st.button('✅ Processar CSV SPT', type='primary'):
                try:
                    perfil = PerfilSPT(nome_sondagem=uploaded_spt.name)
                    medidas = []

                    for _, row in df_spt_upload.iterrows():
                        prof = float(row[c_prof])
                        nspt = int(row[c_nspt])

                        if use_solo_col:
                            raw_solo = row[c_solo]
                            # Try exact match or fallback
                            solo_id = SOLOS_VALIDOS_MAP.get(
                                raw_solo, 'br_solo_residual_geral'
                            )
                        else:
                            solo_id = SOLOS_VALIDOS_MAP.get(default_soil_type)

                        medidas.append((prof, nspt, solo_id))

                    perfil.adicionar_medidas(medidas)
                    st.session_state.perfil_spt = perfil

                    # Update manual editor data too for continuity
                    # Reverse map for display? Or just keep raw?
                    # Simplify: Just update the profile object.

                    st.toast('Perfil SPT carregado!', icon='✅')

                except Exception as e:
                    st.error(f'Erro ao importar: {e}')

    with col_preview:
        st.subheader('Resultado')
        render_active_profile_viz()


# =============================================================================
# TAB 3: IMPORTAR CPT (CSV)
# =============================================================================
with tab_cpt:
    from calculus_core.domain.soil_investigation import (
        PerfilCPT,
        converter_cpt_para_spt,
    )

    col_cpt_imp, col_cpt_viz = st.columns([1, 1], gap='large')

    with col_cpt_imp:
        st.subheader('Importação CPT')

        st.markdown('**Formato esperado (exemplo):**')
        st.code(
            """prof,qc,fs
0.2,1.5,10
0.4,2.0,15
...""",
            language='csv',
        )

        uploaded_cpt = st.file_uploader(
            'Carregar arquivo .csv (CPT)',
            type='csv',
            help='O arquivo deve conter colunas para profundidade, qc e fs.',
            key='cpt_uploader',
        )

        if uploaded_cpt:
            try:
                df_cpt = pd.read_csv(uploaded_cpt)
                st.write('Pré-visualização:')
                st.dataframe(df_cpt.head(), height=150)

                with st.container(border=True):
                    st.markdown('**Mapeamento de Colunas**')
                    coluna_profundidade = st.selectbox(
                        'Profundidade (m)',
                        df_cpt.columns,
                        index=0,
                        key='cpt_col_prof',
                    )
                    coluna_qc = st.selectbox(
                        'Resistência de Ponta qc (MPa)',
                        df_cpt.columns,
                        index=1,
                        key='cpt_col_qc',
                    )
                    coluna_fs = st.selectbox(
                        'Atrito Lateral fs (kPa)',
                        df_cpt.columns,
                        index=2,
                        key='cpt_col_fs',
                    )

                if st.button(
                    'Converter e Definir como Perfil Ativo',
                    type='primary',
                    width='stretch',
                    key='btn_cpt_convert',
                ):
                    try:
                        cpt = PerfilCPT(nome_sondagem=uploaded_cpt.name)
                        medidas = []

                        for _, row in df_cpt.iterrows():
                            medidas.append(
                                (
                                    float(row[coluna_profundidade]),
                                    float(row[coluna_qc]),
                                    float(row[coluna_fs]),
                                )
                            )

                        cpt.adicionar_medidas(medidas)
                        st.session_state.perfil_cpt = cpt  # Store raw CPT

                        # Convert
                        spt_equiv = converter_cpt_para_spt(
                            cpt, 'robertson_1983'
                        )
                        st.session_state.perfil_spt = spt_equiv

                        st.success(
                            f'Conversão concluída! {len(spt_equiv)} camadas geradas.'
                        )
                        # We don't need to ask to go to another page anymore!

                    except Exception as e:
                        st.error(f'Erro ao processar dados: {e}')

            except Exception as e:
                st.error(f'Erro ao ler arquivo: {e}')

    with col_cpt_viz:
        st.subheader('Visualização CPT & SPT Convertido')

        # Show CPT Raw if available
        if st.session_state.get('perfil_cpt'):
            cpt_obj = st.session_state.perfil_cpt
            data_cpt = [
                {'z': m.profundidade, 'qc': m.qc, 'fs': m.fs}
                for m in cpt_obj._medidas
            ]
            df_cpt_viz = pd.DataFrame(data_cpt)

            base = alt.Chart(df_cpt_viz).encode(
                y=alt.Y('z', scale=alt.Scale(reverse=True), title='Prof (m)')
            )

            c_qc = base.mark_line(color='blue').encode(
                x=alt.X('qc', title='qc (MPa)')
            )
            c_fs = base.mark_line(color='green').encode(
                x=alt.X('fs', title='fs (kPa)')
            )

            st.altair_chart(
                (c_qc | c_fs).resolve_scale(y='shared'), width='stretch'
            )

        render_active_profile_viz()
