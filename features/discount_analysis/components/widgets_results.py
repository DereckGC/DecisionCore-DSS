import streamlit as st


_CSS = """
<style>
.result-card {
    background-color: #1a1c24;
    border-radius: 12px;
    padding: 18px 12px;
    text-align: center;
    border: 1px solid #2a2d3a;
    margin-bottom: 15px;
}
.result-card h4 {
    color: #7b808e;
    font-size: 10px;
    margin-bottom: 8px;
    margin-top: 0;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 600;
}
.result-card h3 {
    color: #e5e7eb;
    font-size: 13px;
    margin-bottom: 6px;
    margin-top: 0;
    font-weight: 500;
}
.result-card h2 {
    color: #4f80ff;
    font-size: 22px;
    margin: 0;
    font-weight: bold;
}
.result-card.winner {
    border-color: #4ade80;
    background-color: #142a1e;
}
.result-card.winner h2 {
    color: #4ade80;
}
.section-title {
    color: #e5e7eb;
    font-size: 18px;
    font-weight: bold;
    margin: 28px 0 12px;
    border-left: 5px solid #4f80ff;
    padding-left: 12px;
}
.explanation-box {
    background-color: #1e2029;
    border-left: 4px solid #3b82f6;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 20px;
    font-size: 13.5px;
    color: #d1d5db;
    line-height: 1.5;
}
</style>
"""


def render_results_widgets(res, D):
    st.markdown(_CSS, unsafe_allow_html=True)

    Q_optimo           = res["Q_optimo"]
    nivel_optimo       = res["nivel_optimo"]
    precio_optimo      = res["precio_optimo"]
    costo_total_minimo = res["costo_total_minimo"]
    df_comparativo     = res["tabla_comparativa"]

    st.markdown(
        '<div class="section-title">2. Resultados del Modelo (Cantidad Óptima Q*)</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="result-card winner">
            <h4>Cantidad Óptima (Q*)</h4>
            <h2>{Q_optimo:,.0f}</h2>
            <h3>unidades / orden</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="result-card winner">
            <h4>Costo Total Mínimo</h4>
            <h2>${costo_total_minimo:,.2f}</h2>
            <h3>anual proyectado</h3>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="result-card">
            <h4>Precio Unitario</h4>
            <h2>${precio_optimo:,.2f}</h2>
            <h3>Nivel {nivel_optimo}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="result-card">
            <h4>Frecuencia de Pedidos</h4>
            <h2>{D / Q_optimo:,.1f}</h2>
            <h3>órdenes al año</h3>
        </div>
        """, unsafe_allow_html=True)

    _render_comparative_table(df_comparativo, nivel_optimo)


def _render_comparative_table(df_comparativo, nivel_optimo):
    st.markdown("#### Desglose de Niveles y Costos Comparados")

    def highlight_row(row):
        is_winner = row["Nivel"] == nivel_optimo
        style = "background-color: #142a1e; color: #4ade80; font-weight: bold;"
        return [style if is_winner else "" for _ in row]

    styled_df = df_comparativo.style.apply(highlight_row, axis=1).format({
        "Precio ($)":      "${:,.2f}",
        "Q* Teórico":      "{:,.2f}",
        "Q Real":          "{:,.0f}",
        "Costo Material":  "${:,.2f}",
        "Costo Ordenar":   "${:,.2f}",
        "Costo Almacenar": "${:,.2f}",
        "Costo Total":     "${:,.2f}",
    })

    st.dataframe(styled_df, use_container_width=True, hide_index=True)
