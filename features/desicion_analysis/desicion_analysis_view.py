import streamlit as st
from features.desicion_analysis.components.decision_tables import decision_table
from features.desicion_analysis.components.decision_config import decision_config
from features.desicion_analysis.components.widgets_results import render_results_widgets
from features.desicion_analysis.components.grafics_results import render_results_charts

from features.desicion_analysis.logic.minimax import calculate_minimax
from features.desicion_analysis.logic.maximax import calculate_maximax
from features.desicion_analysis.logic.hurwicz import calculate_hurwicz
from features.desicion_analysis.logic.vme import calculate_vme
from features.desicion_analysis.logic.laplace import calculate_laplace
from features.desicion_analysis.logic.poe import calculate_poe
from features.desicion_analysis.logic.vecip import calculate_vecip
from features.desicion_analysis.logic.veip import calculate_veip

def decision_analysis():
    st.subheader("Analisis de Desición")

    decision_config()
    decision_table()

    if st.button("Obtener Resultados"):
        res_maximax = calculate_maximax(st.session_state.decision_df)
        res_minimax = calculate_minimax(st.session_state.decision_df)

        if res_maximax is not None and res_minimax is not None:
            res_vme = calculate_vme(st.session_state.decision_df)
            res_vecip = calculate_vecip(res_maximax, res_minimax)

            diccionario_resultados = {
                "maximax": res_maximax,
                "minimax": res_minimax,
                "hurwicz": calculate_hurwicz(st.session_state.decision_df, st.session_state.alpha_hurwicz),
                "vme": res_vme,
                "laplace": calculate_laplace(st.session_state.decision_df),
                "poe": calculate_poe(st.session_state.decision_df),
                "vecip": res_vecip,
                "veip": calculate_veip(res_vecip, res_vme)
            }
            st.session_state.decision_results = diccionario_resultados
        else:
            st.error("No hay datos en la tabla para analizar.")

    if "decision_results" in st.session_state:
        render_results_widgets(st.session_state.decision_results)
        render_results_charts(st.session_state.decision_results)
