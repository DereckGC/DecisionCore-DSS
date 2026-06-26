import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_CSS = """
<style>
.inventory-result-card {
    background-color: #1a1c24;
    border-radius: 12px;
    padding: 18px 12px;
    text-align: center;
    border: 1px solid #2a2d3a;
    margin-bottom: 15px;
}
.inventory-result-card h4 {
    color: #7b808e;
    font-size: 10px;
    margin-bottom: 8px;
    margin-top: 0;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 600;
}
.inventory-result-card h3 {
    color: #e5e7eb;
    font-size: 13px;
    margin-bottom: 6px;
    margin-top: 0;
    font-weight: 500;
}
.inventory-result-card h2 {
    color: #4f80ff;
    font-size: 22px;
    margin: 0;
    font-weight: bold;
}
.inventory-result-card.winner {
    border-color: #4ade80;
    background-color: #142a1e;
}
.inventory-result-card.winner h2 {
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
</style>
"""


def _fmt_units(value):
    return f"{value:,.2f}"


def _fmt_money(value):
    if value is None:
        return "No ingresado"
    return f"${value:,.2f}"


def _card(title, value, subtitle, winner=False):
    css_class = "inventory-result-card winner" if winner else "inventory-result-card"
    return f"""
    <div class="{css_class}">
        <h4>{title}</h4>
        <h2>{value}</h2>
        <h3>{subtitle}</h3>
    </div>
    """


def render_inventory_results(res):
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">2. Resultados del Modelo CLE</div>',
        unsafe_allow_html=True,
    )

    row1 = st.columns(4)
    with row1[0]:
        st.markdown(
            _card(
                "Cantidad Optima",
                _fmt_units(res["cantidad_optima"]),
                "unidades por orden",
                winner=True,
            ),
            unsafe_allow_html=True,
        )
    with row1[1]:
        total_subtitle = (
            "incluye compra anual"
            if res["incluye_costo_compra"]
            else "sin costo de compra"
        )
        st.markdown(
            _card(
                "Costo Total",
                _fmt_money(res["costo_total"]),
                total_subtitle,
                winner=True,
            ),
            unsafe_allow_html=True,
        )
    with row1[2]:
        st.markdown(
            _card(
                "Numero de Ordenes",
                _fmt_units(res["numero_ordenes"]),
                "ordenes al ano",
            ),
            unsafe_allow_html=True,
        )
    with row1[3]:
        reorder_value = (
            _fmt_units(res["punto_reorden"])
            if res["punto_reorden"] is not None
            else "No calculado"
        )
        reorder_subtitle = (
            "unidades"
            if res["punto_reorden"] is not None
            else "complete datos de entrega"
        )
        st.markdown(
            _card("Punto de Reorden", reorder_value, reorder_subtitle),
            unsafe_allow_html=True,
        )

    row2 = st.columns(4)
    with row2[0]:
        st.markdown(
            _card(
                "Inventario Maximo",
                _fmt_units(res["inventario_maximo"]),
                "unidades",
            ),
            unsafe_allow_html=True,
        )
    with row2[1]:
        st.markdown(
            _card(
                "Promedio de Inventario",
                _fmt_units(res["promedio_inventario"]),
                "unidades",
            ),
            unsafe_allow_html=True,
        )
    with row2[2]:
        st.markdown(
            _card(
                "Precio Anual Almacenado",
                _fmt_money(res["costo_anual_almacenado"]),
                "costo de mantener inventario",
            ),
            unsafe_allow_html=True,
        )
    with row2[3]:
        st.markdown(
            _card(
                "Precio Anual de Orden",
                _fmt_money(res["costo_anual_orden"]),
                "costo de pedidos",
            ),
            unsafe_allow_html=True,
        )

    _render_eoq_chart(res)
    _render_detail_table(res)

    if not res["opcionales_completos"]:
        st.info(
            "El punto de reorden se calcula cuando ingresa dias laborales, "
            "demanda diaria y tiempo de entrega. El inventario de seguridad "
            "es opcional."
        )

    for warning in res.get("advertencias", []):
        st.warning(warning)


def _render_detail_table(res):
    st.markdown("#### Desglose de costos e inventario")

    rows = [
        {"Indicador": "Cantidad optima por orden (Q*)", "Valor": res["cantidad_optima"]},
        {"Indicador": "Inventario maximo", "Valor": res["inventario_maximo"]},
        {"Indicador": "Promedio de inventario", "Valor": res["promedio_inventario"]},
        {"Indicador": "Numero de ordenes", "Valor": res["numero_ordenes"]},
        {"Indicador": "Costo anual de almacenado", "Valor": res["costo_anual_almacenado"]},
        {"Indicador": "Costo anual de orden", "Valor": res["costo_anual_orden"]},
        {"Indicador": "Costo total operativo", "Valor": res["costo_total_operativo"]},
        {"Indicador": "Costo anual de compra", "Valor": res["costo_anual_compra"]},
        {"Indicador": "Costo total", "Valor": res["costo_total"]},
    ]

    if res["punto_reorden"] is not None:
        rows.insert(0, {"Indicador": "Punto de reorden", "Valor": res["punto_reorden"]})

    df = pd.DataFrame(rows)
    money_rows = {
        "Costo anual de almacenado",
        "Costo anual de orden",
        "Costo total operativo",
        "Costo anual de compra",
        "Costo total",
    }

    def format_value(row):
        if row["Indicador"] in money_rows:
            return _fmt_money(row["Valor"])
        return _fmt_units(row["Valor"])

    df["Valor"] = df.apply(format_value, axis=1)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_eoq_chart(res):
    st.markdown(
        '<div class="section-title">3. Grafica de Costos EOQ</div>',
        unsafe_allow_html=True,
    )

    df = _build_cost_curve(res)
    q_optima = res["cantidad_optima"]
    eoq_total = res["costo_total_relevante"]
    max_y = max(df["Costo total"].max(), eoq_total) * 1.08

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Cantidad"],
            y=df["Costo por ordenar"],
            mode="lines",
            name="Costo por ordenar",
            line={"color": "#155e75", "width": 4},
            hovertemplate="Cantidad: %{x:,.2f}<br>Costo: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Cantidad"],
            y=df["Costo por almacenar"],
            mode="lines",
            name="Costo por almacenar",
            line={"color": "#f97316", "width": 4},
            hovertemplate="Cantidad: %{x:,.2f}<br>Costo: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Cantidad"],
            y=df["Costo total"],
            mode="lines",
            name="Costo total EOQ",
            line={"color": "#166534", "width": 4},
            hovertemplate="Cantidad: %{x:,.2f}<br>Costo: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[q_optima],
            y=[eoq_total],
            mode="markers+text",
            name="EOQ",
            marker={"color": "#0ea5e9", "size": 12, "symbol": "circle"},
            text=[f"EOQ {q_optima:,.2f}"],
            textposition="top center",
            hovertemplate=(
                "EOQ: %{x:,.2f} unidades<br>"
                "Costo total EOQ: $%{y:,.2f}<extra></extra>"
            ),
        )
    )

    fig.add_shape(
        type="line",
        x0=q_optima,
        x1=q_optima,
        y0=0,
        y1=max_y,
        line={"color": "#0ea5e9", "width": 3, "dash": "dot"},
    )
    fig.add_annotation(
        x=q_optima,
        y=0,
        text="EOQ",
        showarrow=False,
        yshift=-18,
        font={"color": "#38bdf8", "size": 12},
    )

    fig.update_layout(
        title="Economic Order Quantity Costs",
        xaxis_title="Cantidad de orden",
        yaxis_title="Costo anual",
        height=460,
        margin={"l": 20, "r": 20, "t": 60, "b": 20},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.28,
            "xanchor": "center",
            "x": 0.5,
        },
        hovermode="x unified",
    )
    fig.update_xaxes(range=[0, df["Cantidad"].max()], gridcolor="#d1d5db")
    fig.update_yaxes(range=[0, max_y], gridcolor="#d1d5db")

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "La grafica EOQ usa el costo relevante de ordenar y almacenar, "
        "sin incluir el costo anual de compra."
    )

    _render_eoq_point_detail(res)


def _build_cost_curve(res):
    q_optima = res["cantidad_optima"]
    max_quantity = max(q_optima * 2.5, q_optima + 10)
    min_quantity = max(1.0, q_optima * 0.1)
    steps = 160
    increment = (max_quantity - min_quantity) / (steps - 1)

    quantities = [min_quantity + (i * increment) for i in range(steps)]
    quantities.append(q_optima)
    quantities = sorted(set(round(quantity, 6) for quantity in quantities))

    rows = []
    for quantity in quantities:
        costo_ordenar = (res["demanda_anual"] / quantity) * res["costo_ordenar"]
        costo_almacenar = (quantity / 2) * res["costo_almacenar"]
        rows.append(
            {
                "Cantidad": quantity,
                "Costo por ordenar": costo_ordenar,
                "Costo por almacenar": costo_almacenar,
                "Costo total": costo_ordenar + costo_almacenar,
            }
        )

    return pd.DataFrame(rows)


def _render_eoq_point_detail(res):
    st.markdown("#### Detalle del punto EOQ")

    df = pd.DataFrame(
        [
            {
                "Cantidad EOQ": _fmt_units(res["cantidad_optima"]),
                "Costo ordenar": _fmt_money(res["costo_anual_orden"]),
                "Costo almacenar EOQ": _fmt_money(
                    res["costo_anual_almacenado_base"]
                ),
                "Costo total EOQ": _fmt_money(res["costo_total_relevante"]),
                "Costo total anual": _fmt_money(res["costo_total"]),
            }
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
