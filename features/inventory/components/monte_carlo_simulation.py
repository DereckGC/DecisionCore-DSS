import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def run_montecarlo_inventory(res, n_sim, dist_type, cv=0.15, range_pct=0.20):
    np.random.seed(42)

    demanda_base = res["demanda_anual"]
    if dist_type == "Normal (Incertidumbre)":
        std_dev = demanda_base * cv
        demandas = np.random.normal(demanda_base, std_dev, n_sim)
    else:
        low = demanda_base * (1 - range_pct)
        high = demanda_base * (1 + range_pct)
        demandas = np.random.uniform(low, high, n_sim)

    demandas = np.clip(demandas, 1, None)
    q_sim = np.sqrt((2 * demandas * res["costo_ordenar"]) / res["costo_almacenar"])
    safety_stock = res["inventario_seguridad"] or 0

    costo_orden = (demandas / q_sim) * res["costo_ordenar"]
    costo_almacenar_base = (q_sim / 2) * res["costo_almacenar"]
    costo_almacenar = ((q_sim / 2) + safety_stock) * res["costo_almacenar"]
    costo_total_operativo = costo_orden + costo_almacenar

    if res["precio_unitario"] is None:
        costo_compra = np.full(n_sim, np.nan)
        costo_total = costo_total_operativo
    else:
        costo_compra = demandas * res["precio_unitario"]
        costo_total = costo_total_operativo + costo_compra

    inventario_maximo = q_sim + safety_stock
    inventario_promedio = (q_sim / 2) + safety_stock
    numero_ordenes = demandas / q_sim
    punto_reorden = None

    if res["punto_reorden"] is not None:
        demanda_diaria_sim = res["demanda_diaria"] * (demandas / demanda_base)
        punto_reorden = (
            demanda_diaria_sim * res["tiempo_entrega"]
        ) + safety_stock

    return {
        "demandas": demandas,
        "q_sim": q_sim,
        "costo_orden": costo_orden,
        "costo_almacenar_base": costo_almacenar_base,
        "costo_almacenar": costo_almacenar,
        "costo_compra": costo_compra,
        "costo_total_operativo": costo_total_operativo,
        "costo_total": costo_total,
        "inventario_maximo": inventario_maximo,
        "inventario_promedio": inventario_promedio,
        "numero_ordenes": numero_ordenes,
        "punto_reorden": punto_reorden,
        "n_sim": n_sim,
        "dist_type": dist_type,
    }


def render_montecarlo_inventory(res):
    st.markdown(
        '<div class="section-title">4. Simulacion Monte Carlo</div>',
        unsafe_allow_html=True,
    )
    st.write(
        f"Se simula la demanda anual alrededor de **{res['demanda_anual']:,.2f}** "
        "unidades y se recalculan los resultados del modelo CLE en cada escenario."
    )
    current_signature = _simulation_signature(res)

    col1, col2 = st.columns(2)
    n_sim = col1.slider(
        "Numero de simulaciones",
        min_value=1000,
        max_value=20000,
        value=5000,
        step=1000,
        key="inventory_mc_n_sim",
    )
    dist_type = col2.selectbox(
        "Distribucion de la demanda",
        ["Normal (Incertidumbre)", "Uniforme (Rango Equitativo)"],
        key="inventory_mc_dist_type",
    )

    col3, _ = st.columns(2)
    cv, range_pct = 0.15, 0.20
    if dist_type == "Normal (Incertidumbre)":
        cv = col3.slider(
            "Coeficiente de variacion",
            min_value=0.05,
            max_value=0.30,
            value=0.15,
            step=0.05,
            key="inventory_mc_cv",
        )
        st.caption(f"Desviacion estandar simulada: {res['demanda_anual'] * cv:,.2f} unidades.")
    else:
        range_pct = col3.slider(
            "Rango de variacion (+/-%)",
            min_value=10,
            max_value=50,
            value=20,
            step=5,
            key="inventory_mc_range_pct",
        ) / 100

    if st.button("Ejecutar simulacion Monte Carlo", use_container_width=True):
        result = run_montecarlo_inventory(
            res,
            n_sim,
            dist_type,
            cv=cv,
            range_pct=range_pct,
        )
        st.session_state.inventory_mc_result = result
        st.session_state.inventory_mc_base = res
        st.session_state.inventory_mc_signature = current_signature

    if "inventory_mc_result" not in st.session_state:
        return

    if st.session_state.get("inventory_mc_signature") != current_signature:
        st.info("Los datos base cambiaron. Ejecute nuevamente la simulacion Monte Carlo.")
        return

    result = st.session_state.inventory_mc_result
    base = st.session_state.inventory_mc_base

    _render_summary(result, base)
    st.divider()
    _render_stats_table(result, base)
    st.divider()
    _render_charts(result, base)
    st.divider()
    _render_insight(result, base)


def _simulation_signature(res):
    return (
        res["demanda_anual"],
        res["costo_ordenar"],
        res["costo_almacenar"],
        res["precio_unitario"],
        res["dias_laborales"],
        res["demanda_diaria"],
        res["tiempo_entrega"],
        res["inventario_seguridad"],
        res["cantidad_optima"],
        res["punto_reorden"],
        res["costo_total"],
    )


def _render_summary(result, base):
    cost_base = base["costo_total"]
    risk_pct = (result["costo_total"] > cost_base).mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("EOQ promedio", f"{np.mean(result['q_sim']):,.2f}")
    col2.metric("Costo promedio", f"${np.mean(result['costo_total']):,.2f}")
    col3.metric("P90 costo total", f"${np.percentile(result['costo_total'], 90):,.2f}")
    col4.metric("Riesgo de exceder base", f"{risk_pct:.1f}%")


def _render_stats_table(result, base):
    st.markdown("#### Estadisticas simuladas")

    simulated_results = {
        "Demanda anual": result["demandas"],
        "Cantidad EOQ": result["q_sim"],
        "Inventario maximo": result["inventario_maximo"],
        "Promedio de inventario": result["inventario_promedio"],
        "Numero de ordenes": result["numero_ordenes"],
        "Costo anual de orden": result["costo_orden"],
        "Costo anual de almacenado": result["costo_almacenar"],
        "Costo total operativo": result["costo_total_operativo"],
        "Costo total": result["costo_total"],
    }

    if base["precio_unitario"] is not None:
        simulated_results["Costo anual de compra"] = result["costo_compra"]
    if result["punto_reorden"] is not None:
        simulated_results["Punto de reorden"] = result["punto_reorden"]

    rows = []
    money_rows = {
        "Costo anual de orden",
        "Costo anual de almacenado",
        "Costo total operativo",
        "Costo anual de compra",
        "Costo total",
    }

    for name, values in simulated_results.items():
        is_money = name in money_rows
        rows.append(
            {
                "Resultado": name,
                "Promedio": _format_stat(np.mean(values), is_money),
                "Desv. estandar": _format_stat(np.std(values), is_money),
                "Minimo": _format_stat(np.min(values), is_money),
                "P10": _format_stat(np.percentile(values, 10), is_money),
                "Mediana": _format_stat(np.percentile(values, 50), is_money),
                "P90": _format_stat(np.percentile(values, 90), is_money),
                "Maximo": _format_stat(np.max(values), is_money),
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def _format_stat(value, is_money=False):
    if is_money:
        return f"${value:,.2f}"
    return f"{value:,.2f}"


def _render_charts(result, base):
    col1, col2 = st.columns(2)

    with col1:
        fig_cost = go.Figure()
        fig_cost.add_trace(
            go.Histogram(
                x=result["costo_total"],
                nbinsx=45,
                marker_color="#3b82f6",
                name="Costo total",
            )
        )
        fig_cost.add_vline(
            x=base["costo_total"],
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="Base",
        )
        fig_cost.update_layout(
            title="Distribucion de costo total",
            xaxis_title="Costo total anual",
            yaxis_title="Frecuencia",
            height=360,
            margin={"l": 20, "r": 20, "t": 50, "b": 20},
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    with col2:
        fig_eoq = go.Figure()
        fig_eoq.add_trace(
            go.Histogram(
                x=result["q_sim"],
                nbinsx=45,
                marker_color="#10b981",
                name="EOQ",
            )
        )
        fig_eoq.add_vline(
            x=base["cantidad_optima"],
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="EOQ base",
        )
        fig_eoq.update_layout(
            title="Distribucion de cantidad optima EOQ",
            xaxis_title="Cantidad optima",
            yaxis_title="Frecuencia",
            height=360,
            margin={"l": 20, "r": 20, "t": 50, "b": 20},
        )
        st.plotly_chart(fig_eoq, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig_scatter = go.Figure()
        fig_scatter.add_trace(
            go.Scatter(
                x=result["demandas"],
                y=result["costo_total"],
                mode="markers",
                marker={
                    "color": result["q_sim"],
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": "EOQ"},
                    "size": 6,
                    "opacity": 0.55,
                },
                name="Escenarios",
                hovertemplate=(
                    "Demanda: %{x:,.2f}<br>"
                    "Costo total: $%{y:,.2f}<extra></extra>"
                ),
            )
        )
        fig_scatter.update_layout(
            title="Demanda simulada vs costo total",
            xaxis_title="Demanda anual",
            yaxis_title="Costo total",
            height=380,
            margin={"l": 20, "r": 20, "t": 50, "b": 20},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col4:
        fig_components = go.Figure()
        fig_components.add_trace(
            go.Box(
                y=result["costo_orden"],
                name="Ordenar",
                marker_color="#155e75",
                boxmean=True,
            )
        )
        fig_components.add_trace(
            go.Box(
                y=result["costo_almacenar"],
                name="Almacenar",
                marker_color="#f97316",
                boxmean=True,
            )
        )
        fig_components.add_trace(
            go.Box(
                y=result["costo_total_operativo"],
                name="Total operativo",
                marker_color="#166534",
                boxmean=True,
            )
        )
        fig_components.update_layout(
            title="Variacion de componentes de costo",
            yaxis_title="Costo anual",
            height=380,
            margin={"l": 20, "r": 20, "t": 50, "b": 20},
        )
        st.plotly_chart(fig_components, use_container_width=True)

    if result["punto_reorden"] is not None:
        _render_reorder_chart(result, base)


def _render_reorder_chart(result, base):
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=result["punto_reorden"],
            nbinsx=45,
            marker_color="#8b5cf6",
            name="Punto de reorden",
        )
    )
    fig.add_vline(
        x=base["punto_reorden"],
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="PRO base",
    )
    fig.update_layout(
        title="Distribucion de punto de reorden simulado",
        xaxis_title="Punto de reorden",
        yaxis_title="Frecuencia",
        height=360,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_insight(result, base):
    mean_total = np.mean(result["costo_total"])
    risk_pct = (result["costo_total"] > base["costo_total"]).mean() * 100
    mean_q = np.mean(result["q_sim"])

    st.info(
        f"Con la demanda simulada, la cantidad EOQ promedio fue **{mean_q:,.2f}** "
        f"unidades y el costo total promedio fue **${mean_total:,.2f}**. "
        f"El **{risk_pct:.1f}%** de los escenarios supera el costo base "
        f"de **${base['costo_total']:,.2f}**."
    )
