import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from features.forecast.logic.wma import calculate_wma
from features.forecast.logic.exponential_smoothing import (
    calculate_exponential_smoothing
)
from features.forecast.logic.forecast_comparison import compare_methods
from features.forecast.logic.monte_carlo import monte_carlo_forecast

from features.forecast.components.comparison_component import display_comparison
from features.forecast.components.forecast_styles import load_forecast_styles


def _fmt(value):
    return f"{value:,.2f}"


def _card(title, value, subtitle, winner=False):
    css = "forecast-result-card winner" if winner else "forecast-result-card"
    return f"""
    <div class="{css}">
        <h4>{title}</h4>
        <h2>{value}</h2>
        <h3>{subtitle}</h3>
    </div>
    """

def forecast_view():

    load_forecast_styles()

    st.subheader("Modelo de Pronósticos")

    st.markdown(
        '<div class="section-title">1. Datos Históricos</div>',
        unsafe_allow_html=True,
    )

    data_text = st.text_area(
        "Ingresa valores separados por comas",
        placeholder="Ejemplo: 10, 12, 15, 14, 18, 20",
        height=120
    )

    if st.button("Cargar datos"):

        try:
            data = [
                float(x.strip())
                for x in data_text.split(",")
                if x.strip()
            ]

            if len(data) < 2:
                st.error("Ingresa al menos 2 datos")
                return

            st.session_state.data = data
            st.session_state.show_results = False

            st.success("Datos cargados")

        except:
            st.error("Error en formato de datos")

    if "data" not in st.session_state:
        return

    data = st.session_state.data

    st.dataframe(pd.DataFrame(data, columns=["Valor"]))

    st.markdown(
        '<div class="section-title">2. Configuración del modelo</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        max_period = max(2, min(20, len(data) - 1))

        wma_period = st.slider("Periodo WMA", 2, max_period, 3)
        alpha = st.slider("Alpha (ES)", 0.0, 1.0, 0.3)

    with col2:

        initial_forecast = st.number_input(
            "Forecast inicial",
            value=float(data[0])
        )

        run = st.button("Analizar")

    if run:

        st.session_state.wma_period = wma_period
        st.session_state.alpha = alpha
        st.session_state.initial_forecast = initial_forecast

        st.session_state.show_results = True

    if st.session_state.get("show_results", False):

        st.markdown(
            '<div class="section-title">3. Resultados</div>',
            unsafe_allow_html=True,
        )

        wma_values = calculate_wma(data, st.session_state.wma_period)
        es_values = calculate_exponential_smoothing(
            data,
            st.session_state.alpha,
            st.session_state.initial_forecast
        )

        metrics_df, results = compare_methods(data, wma_values, es_values)

        display_comparison(data, {"WMA": wma_values, "ES": es_values}, metrics_df)

        st.markdown(
            '<div class="section-title">4. Métricas del modelo</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                _card(
                    "MAD WMA",
                    _fmt(results["WMA"]["MAD"]),
                    "Error promedio absoluto",
                    winner=True
                ),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                _card(
                    "MAD ES",
                    _fmt(results["ES"]["MAD"]),
                    "Error promedio absoluto",
                    winner=True
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-title">5. Pronóstico siguiente período</div>',
            unsafe_allow_html=True,
        )

        last_values = data[-st.session_state.wma_period:]
        weights = np.arange(1, st.session_state.wma_period + 1)

        next_wma = np.sum(np.array(last_values) * weights) / weights.sum()

        next_es = (
            st.session_state.alpha * data[-1]
            + (1 - st.session_state.alpha) * es_values[-1]
        )

        st.session_state.next_wma = next_wma
        st.session_state.next_es = next_es

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                _card("WMA", f"{next_wma:.2f}", "Pronóstico"),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                _card("ES", f"{next_es:.2f}", "Pronóstico"),
                unsafe_allow_html=True,
            )

        best_method = "WMA" if results["WMA"]["MAD"] < results["ES"]["MAD"] else "ES"

        st.info(
            f"""
            El modelo con mejor desempeño es {best_method}, ya que presenta el menor error promedio (MAD)
            en comparación con los datos históricos. Se recomienda utilizar este modelo para la toma de decisiones y planificación del siguiente período,
            debido a que se ajusta mejor al comportamiento observado de la serie de datos.
            """
        )

        # MONTE CARLO

        st.markdown(
            '<div class="section-title">6. Simulación Monte Carlo</div>',
            unsafe_allow_html=True,
        )

        if st.button("Ejecutar simulación"):

            wma_mc = monte_carlo_forecast(next_wma, results["WMA"]["deviations"])
            es_mc = monte_carlo_forecast(next_es, results["ES"]["deviations"])

            st.markdown("#### Indicadores clave de incertidumbre")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    _card(
                        "WMA - Valor esperado",
                        f"{wma_mc['mean']:.2f}",
                        f"Rango: {wma_mc['min']:.2f} - {wma_mc['max']:.2f}"
                    ),
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    _card(
                        "ES - Valor esperado",
                        f"{es_mc['mean']:.2f}",
                        f"Rango: {es_mc['min']:.2f} - {es_mc['max']:.2f}"
                    ),
                    unsafe_allow_html=True,
                )

            def risk_level(min_v, max_v, mean_v):
                spread = (max_v - min_v) / mean_v
                if spread < 0.10:
                    return "Bajo"
                elif spread < 0.25:
                    return "Moderado"
                else:
                    return "Alto"

            wma_risk = risk_level(wma_mc["min"], wma_mc["max"], wma_mc["mean"])
            es_risk = risk_level(es_mc["min"], es_mc["max"], es_mc["mean"])

            st.markdown("#### Nivel de riesgo del pronóstico")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    _card("WMA - Riesgo", wma_risk, "Basado en variabilidad"),
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(
                    _card("ES - Riesgo", es_risk, "Basado en variabilidad"),
                    unsafe_allow_html=True,
                )

            st.markdown("#### Rango de incertidumbre")

            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Bar(
                name="Mínimo",
                x=["WMA", "ES"],
                y=[wma_mc["min"], es_mc["min"]],
            ))

            fig.add_trace(go.Bar(
                name="Promedio",
                x=["WMA", "ES"],
                y=[wma_mc["mean"], es_mc["mean"]],
            ))

            fig.add_trace(go.Bar(
                name="Máximo",
                x=["WMA", "ES"],
                y=[wma_mc["max"], es_mc["max"]],
            ))

            fig.update_layout(
                barmode="group",
                title="Escenarios de incertidumbre",
                xaxis_title="Modelo",
                yaxis_title="Valor del pronóstico",
                height=420
            )

            st.plotly_chart(fig, use_container_width=True)


            better = "WMA" if (wma_mc["max"] - wma_mc["min"]) < (es_mc["max"] - es_mc["min"]) else "ES"

            st.success(
                f"""
                La simulación Monte Carlo indica que la demanda futura presenta variabilidad alrededor del pronóstico. El modelo WMA muestra un valor esperado de {wma_mc['mean']:.2f} con un nivel de riesgo {wma_risk.lower()},
                mientras que el modelo ES presenta un valor esperado de {es_mc['mean']:.2f} con riesgo {es_risk.lower()}. El modelo más estable es {better}, debido a una menor dispersión en sus resultados. Se recomienda para la planificación considerar estos rangos de variación para reducir el riesgo
                de sobrestock o desabastecimiento.
                """
            )
 