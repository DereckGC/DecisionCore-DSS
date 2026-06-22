import streamlit as st


def discount_config():
    col1, col2 = st.columns(2)

    forecast_demand = st.session_state.get("forecast_annual_demand", None)

    if forecast_demand is not None:
        import_forecast = col1.checkbox("Importar demanda desde Pronósticos", value=True)
        if import_forecast:
            D = col1.number_input(
                "Demanda Anual (D) [Importada]",
                value=float(forecast_demand),
                disabled=True,
                format="%.2f"
            )
        else:
            D = col1.number_input(
                "Demanda Anual (D)",
                min_value=0.0,
                value=None,
                placeholder="Ingrese la demanda anual (D)",
                format="%.2f"
            )
    else:
        D = col1.number_input(
            "Demanda Anual (D)",
            min_value=0.0,
            value=None,
            placeholder="Ingrese la demanda anual (D)",
            format="%.2f"
        )

    Co = col2.number_input(
        "Costo por Ordenar (Co)",
        min_value=0.0,
        value=None,
        placeholder="Ingrese el costo por ordenar (Co)",
        format="%.2f"
    )

    col3, col4 = st.columns(2)
    holding_type = col3.selectbox(
        "Costo de Almacenamiento",
        [
            "Tasa de almacenamiento (I) [% del precio]",
            "Costo fijo unitario anual (Ch)"
        ]
    )
    is_percentage = (holding_type == "Tasa de almacenamiento (I) [% del precio]")

    if is_percentage:
        holding_value = col4.number_input(
            "Tasa de Almacenamiento (I) [ej: 0.20 para 20%]",
            min_value=0.0,
            max_value=1.0,
            value=None,
            placeholder="Ej: 0.20",
            format="%.4f"
        )
    else:
        holding_value = col4.number_input(
            "Costo fijo anual por almacenar (Ch)",
            min_value=0.0,
            value=None,
            placeholder="Ingrese costo de almacenamiento (Ch)",
            format="%.2f"
        )

    return D, Co, holding_value, is_percentage
