import streamlit as st

from features.discount_analysis.components.discount_config import discount_config
from features.discount_analysis.components.discounts_table import render_discounts_table
from features.discount_analysis.components.widgets_results import render_results_widgets
from features.discount_analysis.components.monte_carlo_simulation import render_montecarlo_descuento
from features.discount_analysis.logic.cle import calcular_descuento_cantidad


def discount_analysis_view():
    st.subheader("Modelos de Inventarios: Descuentos por Cantidad")

    st.markdown(
        '<div class="section-title">1. Parámetros de Entrada y Tabla de Descuentos</div>',
        unsafe_allow_html=True
    )
    D, Co, holding_value, is_percentage = discount_config()

    valid_table, table_msg = render_discounts_table()

    if D is None or Co is None or holding_value is None:
        st.info("💡 Por favor, ingrese todos los parámetros de entrada (Demanda Anual, Costo por Ordenar y Costo de Almacenamiento) para comenzar.")
        return

    if D <= 0 or Co <= 0 or holding_value <= 0:
        st.error("⚠️ Los parámetros de entrada deben ser mayores a cero.")
        return

    if not valid_table:
        st.warning("Configure correctamente la tabla de descuentos para calcular los resultados.")
        return

    discount_rows = [
        {"min_qty": r["Cantidad Mínima"], "price": r["Precio Unitario"]}
        for _, r in st.session_state.discount_df.iterrows()
    ]
    res = calcular_descuento_cantidad(D, Co, holding_value, is_percentage, discount_rows)

    if res.get("error"):
        st.error(res["error"])
        return

    render_results_widgets(res, D)

    render_montecarlo_descuento(
        D, Co, holding_value, is_percentage,
        res["precio_optimo"], res["Q_optimo"],
        res["costo_total_minimo"], res["nivel_optimo"]
    )