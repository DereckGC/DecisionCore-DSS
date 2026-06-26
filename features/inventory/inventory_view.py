import streamlit as st

from features.inventory.components.inventory_table import render_inventory_results
from features.inventory.components.monte_carlo_simulation import (
    render_montecarlo_inventory,
)
from features.inventory.logic.cle import calcular_cle


_SECTION_CSS = """
<style>
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


def _number_input(container, label, placeholder, key, min_value=0.0):
    return container.number_input(
        label,
        min_value=min_value,
        value=None,
        placeholder=placeholder,
        format="%.2f",
        key=key,
    )


def _render_required_inputs():
    col1, col2 = st.columns(2)
    forecast_demand = st.session_state.get("forecast_annual_demand", None)

    if forecast_demand is not None:
        import_forecast = col1.checkbox("Importar demanda desde Pronosticos", value=True)
        if import_forecast:
            demanda_anual = col1.number_input(
                "Demanda Anual (D) [Importada]",
                value=float(forecast_demand),
                disabled=True,
                format="%.2f",
                key="inventory_demanda_importada",
            )
        else:
            demanda_anual = _number_input(
                col1,
                "Demanda Anual (D)",
                "Ingrese la demanda anual",
                "inventory_demanda_anual",
            )
    else:
        demanda_anual = _number_input(
            col1,
            "Demanda Anual (D)",
            "Ingrese la demanda anual",
            "inventory_demanda_anual",
        )

    costo_ordenar = _number_input(
        col2,
        "Costo por Ordenar (Co)",
        "Ingrese el costo por orden",
        "inventory_costo_ordenar",
    )

    col3, col4 = st.columns(2)
    costo_almacenar = _number_input(
        col3,
        "Costo por Almacenar (Ch)",
        "Costo anual por unidad almacenada",
        "inventory_costo_almacenar",
    )
    precio_unitario = _number_input(
        col4,
        "Precio Unitario (Cu) [Opcional]",
        "Opcional para incluir costo anual de compra",
        "inventory_precio_unitario",
    )

    return demanda_anual, costo_ordenar, costo_almacenar, precio_unitario


def _render_optional_inputs():
    st.markdown(
        '<div class="section-title">Parametros Opcionales para Punto de Reorden</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    dias_laborales = _number_input(
        col1,
        "Dias Laborales por Ano",
        "Ej: 250",
        "inventory_dias_laborales",
    )
    demanda_diaria = _number_input(
        col2,
        "Demanda Diaria",
        "Ingrese la demanda diaria",
        "inventory_demanda_diaria",
    )

    col3, col4 = st.columns(2)
    tiempo_entrega = _number_input(
        col3,
        "Tiempo de Entrega",
        "Dias de entrega",
        "inventory_tiempo_entrega",
    )
    inventario_seguridad = _number_input(
        col4,
        "Inventario de Seguridad",
        "Unidades de seguridad",
        "inventory_inventario_seguridad",
    )

    return dias_laborales, demanda_diaria, tiempo_entrega, inventario_seguridad


def inventory_view():
    st.markdown(_SECTION_CSS, unsafe_allow_html=True)
    st.subheader("Modelo de Inventarios: Cantidad de Lote Economico (CLE)")

    st.markdown(
        '<div class="section-title">1. Parametros de Entrada</div>',
        unsafe_allow_html=True,
    )

    (
        demanda_anual,
        costo_ordenar,
        costo_almacenar,
        precio_unitario,
    ) = _render_required_inputs()

    (
        dias_laborales,
        demanda_diaria,
        tiempo_entrega,
        inventario_seguridad,
    ) = _render_optional_inputs()

    required_values = [
        demanda_anual,
        costo_ordenar,
        costo_almacenar,
    ]

    if any(value is None for value in required_values):
        st.info(
            "Ingrese demanda anual, costo por ordenar y costo por almacenar "
            "para calcular el CLE. El precio unitario es opcional."
        )
        return

    res = calcular_cle(
        demanda_anual=demanda_anual,
        costo_ordenar=costo_ordenar,
        costo_almacenar=costo_almacenar,
        precio_unitario=precio_unitario,
        dias_laborales=dias_laborales,
        demanda_diaria=demanda_diaria,
        tiempo_entrega=tiempo_entrega,
        inventario_seguridad=inventario_seguridad,
    )

    if res.get("error"):
        st.error(res["error"])
        return

    render_inventory_results(res)
    render_montecarlo_inventory(res)
