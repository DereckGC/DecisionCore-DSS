import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from features.forecast.logic.wma import calculate_wma
from features.forecast.logic.exponential_smoothing import (
    calculate_exponential_smoothing
)
from features.forecast.logic.forecast_comparison import (
    compare_methods
)
from features.forecast.logic.monte_carlo import (
    monte_carlo_forecast
)
from features.forecast.components.comparison_component import (
    display_comparison
)


def forecast_view():

    st.header("Análisis de Pronósticos")

    st.subheader("Ingresa datos históricos")

    data_text = st.text_area(
        "Escribe los valores separados por comas",
        height=150
    )

    if st.button("Cargar datos"):

        data_list = [
            float(x.strip())
            for x in data_text.split(",")
            if x.strip()
        ]

        st.session_state.data = data_list
        st.session_state.mostrar_resultados = False
        st.success("Datos cargados")

    if 'data' in st.session_state and st.session_state.data:

        data = st.session_state.data

        st.divider()

        st.write("Datos:")
        st.dataframe(pd.DataFrame(data, columns=["Valor"]))

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            wma_period = st.slider("WMA Period", 2, min(20, len(data)-1), 3)

            alpha = st.slider("Alpha", 0.0, 1.0, 0.3)

        with col2:
            initial_forecast = st.number_input(
                "Forecast inicial",
                value=float(data[0])
            )

            analizar = st.button("Analizar")

        if analizar:
            st.session_state.mostrar_resultados = True
            st.session_state.wma_period = wma_period
            st.session_state.alpha = alpha
            st.session_state.initial_forecast = initial_forecast

        if st.session_state.get("mostrar_resultados", False):

            st.divider()

            st.markdown("## Modelos de Pronóstico")

            wma_values = calculate_wma(
                data,
                st.session_state.wma_period
            )

            es_values = calculate_exponential_smoothing(
                data,
                st.session_state.alpha,
                st.session_state.initial_forecast
            )

            metrics_df, results = compare_methods(
                data,
                wma_values,
                es_values
            )

            display_comparison(
                data,
                {'WMA': wma_values, 'ES': es_values},
                metrics_df
            )

            st.divider()

            st.markdown("## Evaluación de Error")

            st.subheader("Desviaciones")

            c1, c2 = st.columns(2)

            with c1:
                st.metric("WMA DMA", results['WMA']['MAD'])

            with c2:
                st.metric("ES DMA", results['ES']['MAD'])

            st.divider()

            st.markdown("## Predicción del Próximo Período")

            st.subheader("Pronóstico próximo período")

            last_values = data[-st.session_state.wma_period:]
            weights = np.arange(1, st.session_state.wma_period + 1)

            next_wma = np.sum(np.array(last_values) * weights) / weights.sum()

            next_es = (
                st.session_state.alpha * data[-1]
                + (1 - st.session_state.alpha) * es_values[-1]
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric("WMA", f"{next_wma:.2f}")

            with col2:
                st.metric("ES", f"{next_es:.2f}")

        # MONTE CARLO

        if (
            st.session_state.get("mostrar_resultados", False)
            and 'data' in st.session_state
        ):
            
            st.markdown("## Simulación Monte Carlo")

            run_mc = st.button("Ejecutar Monte Carlo")

            if run_mc:

                wma_mc = monte_carlo_forecast(
                    next_wma,
                    results['WMA']['deviations']
                )

                es_mc = monte_carlo_forecast(
                    next_es,
                    results['ES']['deviations']
                )

                st.divider()

                st.subheader("Monte Carlo (10,000 simulaciones)")

                mc1, mc2 = st.columns(2)

                with mc1:
                    st.write("WMA")
                    st.metric("Promedio", f"{wma_mc['mean']:.2f}")
                    st.metric("Min", f"{wma_mc['min']:.2f}")
                    st.metric("Max", f"{wma_mc['max']:.2f}")

                with mc2:
                    st.write("ES")
                    st.metric("Promedio", f"{es_mc['mean']:.2f}")
                    st.metric("Min", f"{es_mc['min']:.2f}")
                    st.metric("Max", f"{es_mc['max']:.2f}")

                st.divider()

                st.subheader("Distribución")

                fig, ax = plt.subplots(figsize=(10, 5))

                ax.hist(wma_mc['values'], bins=30, alpha=0.6, label="WMA")
                ax.hist(es_mc['values'], bins=30, alpha=0.6, label="ES")

                ax.legend()
                st.pyplot(fig)
