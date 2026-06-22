import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def run_montecarlo_descuento(D, Co, holding_value, is_percentage, precio_optimo, Q_optimo, n_sim, dist_type, cv=0.15, range_pct=0.20):
    np.random.seed(42)

    if dist_type == "Normal (Incertidumbre)":
        std_dev = D * cv
        demands_sim = np.random.normal(D, std_dev, n_sim)
    else:
        demands_sim = np.random.uniform(D * (1 - range_pct), D * (1 + range_pct), n_sim)

    demands_sim = np.clip(demands_sim, 1, None)

    Ch_opt = holding_value * precio_optimo if is_percentage else holding_value
    costs_sim = (
        demands_sim * precio_optimo
        + (demands_sim / Q_optimo) * Co
        + (Q_optimo / 2) * Ch_opt
    )

    return {
        "demands_sim": demands_sim,
        "costs_sim":   costs_sim,
        "mean_c":      float(np.mean(costs_sim)),
        "std_c":       float(np.std(costs_sim)),
        "min_c":       float(np.min(costs_sim)),
        "max_c":       float(np.max(costs_sim)),
        "p10":         float(np.percentile(costs_sim, 10)),
        "median_c":    float(np.percentile(costs_sim, 50)),
        "p90":         float(np.percentile(costs_sim, 90)),
    }


def render_montecarlo_descuento(D, Co, holding_value, is_percentage, precio_optimo, Q_optimo, costo_total_minimo, nivel_optimo):
    st.markdown('<div class="section-title">3. Simulación de Riesgo de Demanda (Monte Carlo)</div>', unsafe_allow_html=True)
    st.write(
        f"Manteniendo la decisión fija de ordenar **Q* = {Q_optimo:,.0f}** "
        f"a un precio de **\\${precio_optimo:.2f}**, simulamos qué ocurre con el "
        f"costo si la demanda anual cambia."
    )

    col_mc1, col_mc2 = st.columns(2)
    n_sim = col_mc1.slider(
        "Número de Simulaciones",
        min_value=1000, max_value=10000, value=5000, step=1000
    )
    dist_type = col_mc2.selectbox(
        "Distribución de la Demanda",
        ["Normal (Incertidumbre)", "Uniforme (Rango Equitativo)"]
    )

    col_mc3, _ = st.columns(2)
    cv, range_pct = 0.15, 0.20
    if dist_type == "Normal (Incertidumbre)":
        cv = col_mc3.slider(
            "Coeficiente de Variación (Volatilidad de demanda)",
            min_value=0.05, max_value=0.30, value=0.15, step=0.05
        )
        st.caption(f"Desviación estándar calculada: **{D * cv:,.2f}** unidades.")
    else:
        range_pct = col_mc3.slider(
            "Rango de Variación (±%) alrededor de la demanda",
            min_value=10, max_value=50, value=20, step=5
        ) / 100

    if st.button("▶ Ejecutar Simulación de Riesgo", use_container_width=True):
        result = run_montecarlo_descuento(
            D, Co, holding_value, is_percentage,
            precio_optimo, Q_optimo,
            n_sim, dist_type, cv, range_pct
        )
        st.session_state.discount_mc_result      = result
        st.session_state.discount_mc_costo_base  = costo_total_minimo
        st.session_state.discount_mc_Q           = Q_optimo
        st.session_state.discount_mc_precio      = precio_optimo

    if "discount_mc_result" not in st.session_state:
        return

    result     = st.session_state.discount_mc_result
    costo_base = st.session_state.discount_mc_costo_base
    costs_sim  = result["costs_sim"]

    risk_pct = (costs_sim > costo_base).mean() * 100

    _render_kpis(result, risk_pct)
    st.divider()
    _render_stats_table(result)
    st.divider()
    _render_charts(costs_sim, costo_base)
    st.divider()
    _render_insight(
        st.session_state.discount_mc_Q,
        st.session_state.discount_mc_precio,
        result["mean_c"],
        risk_pct,
        costo_base
    )


def _render_kpis(result, risk_pct):
    col1, col2, col3 = st.columns(3)
    col1.metric("Costo Promedio Simulado", f"${result['mean_c']:,.2f}")
    col2.metric("Desviación Estándar",     f"${result['std_c']:,.2f}")
    col3.metric("Riesgo de Exceder Presupuesto", f"{risk_pct:.1f}%")


def _render_stats_table(result):
    st.markdown("#### Estadísticas de Riesgo")
    stat_df = pd.DataFrame({
        "Métrica / Percentil": ["Mínimo", "Percentil 10%", "Mediana (P50)", "Percentil 90%", "Máximo"],
        "Costo Total Simulado": [
            result["min_c"], result["p10"],
            result["median_c"], result["p90"], result["max_c"]
        ]
    })
    st.dataframe(
        stat_df.style.format({"Costo Total Simulado": "${:,.2f}"}),
        use_container_width=True,
        hide_index=True
    )


def _render_charts(costs_sim, costo_base):
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_hist = px.histogram(
            x=costs_sim,
            nbins=40,
            color_discrete_sequence=["#3b82f6"],
            title="Frecuencia de Costo Total Simulado"
        )
        fig_hist.add_vline(
            x=costo_base, line_dash="dash", line_color="#ef4444",
            line_width=2, annotation_text="Costo Determinista"
        )
        fig_hist.update_layout(
            xaxis_title="Costo Total Anual ($)",
            yaxis_title="Casos",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_g2:
        sorted_costs = np.sort(costs_sim)
        cdf = np.arange(1, len(sorted_costs) + 1) / len(sorted_costs)

        fig_cdf = go.Figure()
        fig_cdf.add_trace(go.Scatter(
            x=sorted_costs,
            y=cdf * 100,
            mode="lines",
            line=dict(color="#10b981", width=3),
            name="Prob. Acumulada"
        ))
        fig_cdf.add_vline(
            x=costo_base, line_dash="dash", line_color="#ef4444",
            line_width=2, annotation_text="Presupuesto"
        )
        fig_cdf.update_layout(
            title="Curva S de Probabilidad Acumulada",
            xaxis_title="Costo Total Anual ($)",
            yaxis_title="Probabilidad Acumulada (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        )
        fig_cdf.update_xaxes(showgrid=True, gridcolor="#2a2d3a")
        fig_cdf.update_yaxes(showgrid=True, gridcolor="#2a2d3a")
        st.plotly_chart(fig_cdf, use_container_width=True)


def _render_insight(Q_optimo, precio_optimo, mean_c, risk_pct, costo_base):
    st.info(
        f"💡 Comprar lotes de **{Q_optimo:,.0f}** unidades al precio de "
        f"**\\${precio_optimo:.2f}** resulta en un costo promedio estimado de "
        f"**\\${mean_c:,.2f}**. Debido a la variabilidad aleatoria de la demanda, "
        f"existe un **{risk_pct:.1f}%** de riesgo de que el costo real sea mayor "
        f"que el presupuesto de **\\${costo_base:,.2f}**."
    )
