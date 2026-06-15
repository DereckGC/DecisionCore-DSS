import streamlit as st
import pandas as pd
import numpy as np

from features.forecast.logic.wma import calculate_wma
from features.forecast.logic.exponential_smoothing import (
    calculate_exponential_smoothing
)
from features.forecast.logic.forecast_comparison import (
    compare_methods
)
from features.forecast.components.comparison_component import (
    display_comparison
)

def forecast_view():
    st.header("Análisis de Pronósticos")

    st.subheader("Ingresa datos históricos")

    data_text = st.text_area(
        "Escribe los valores separados por comas (ej: 10, 12, 15, 14, 18)",
        height=150,
        placeholder="10, 12, 15, 14, 18, 20, 19, 22, 25, 24, 28, 30"
    )

    if st.button("Cargar datos", use_container_width=True):
        try:
            data_list = [
                float(x.strip())
                for x in data_text.split(",")
                if x.strip()
            ]

            if len(data_list) < 4:
                st.error("Debes ingresar al menos 4 datos.")
                return

            st.session_state.data = data_list
            st.session_state.mostrar_resultados = False

            st.success(
                f"{len(data_list)} valores cargados"
            )

        except ValueError:
            st.error(
                "Error: asegúrate de separar los valores por comas"
            )

    if 'data' in st.session_state and st.session_state.data:

        st.divider()

        st.subheader("Datos cargados:")

        df_display = pd.DataFrame({
            'Período': range(
                1,
                len(st.session_state.data) + 1
            ),
            'Valor': st.session_state.data
        })

        st.dataframe(
            df_display,
            use_container_width=True
        )

        data = st.session_state.data

        st.write(
            f"**Total de registros:** {len(data)}"
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            wma_period = st.slider(
                "Período WMA",
                min_value=2,
                max_value=min(20, len(data) - 1),
                value=min(3, len(data) - 1),
                key="wma_slider"
            )

            alpha = st.slider(
                "Alpha (Suavizamiento)",
                0.0,
                1.0,
                0.3,
                step=0.05,
                key="alpha_slider"
            )

        with col2:
            initial_forecast = st.number_input(
                "Pronóstico Inicial (ES)",
                value=float(data[0]),
                key="initial_forecast"
            )

            st.write("")
            st.write("")

            analizar = st.button(
                "Analizar",
                use_container_width=True
            )

        if analizar:
            st.session_state.mostrar_resultados = True
            st.session_state.wma_period_saved = wma_period
            st.session_state.alpha_saved = alpha
            st.session_state.initial_forecast_saved = initial_forecast

        if st.session_state.get(
            'mostrar_resultados',
            False
        ):
            try:

                st.divider()

                wma_values = calculate_wma(
                    data,
                    st.session_state.wma_period_saved
                )

                es_values = calculate_exponential_smoothing(
                    data,
                    st.session_state.alpha_saved,
                    st.session_state.initial_forecast_saved
                )

                methods_data = {
                    'WMA': wma_values,
                    'ES': es_values
                }

                metrics_df, results = compare_methods(
                    data,
                    wma_values,
                    es_values
                )

                display_comparison(
                    data,
                    methods_data,
                    metrics_df
                )

                st.divider()

                st.subheader(
                    "Desviaciones (DMA)"
                )

                det_col1, det_col2 = st.columns(2)

                with det_col1:
                    st.metric(
                        "WMA - DMA",
                        f"{results['WMA']['MAD']:.4f}"
                    )

                with det_col2:
                    st.metric(
                        "ES - DMA",
                        f"{results['ES']['MAD']:.4f}"
                    )

                st.divider()

                st.subheader(
                    "Pronóstico para el Próximo Período"
                )

                last_values = data[
                    -st.session_state.wma_period_saved:
                ]

                weights = np.arange(
                    1,
                    st.session_state.wma_period_saved + 1
                )

                next_wma = (
                    np.sum(
                        np.array(last_values) * weights
                    )
                    / weights.sum()
                )

                next_es = (
                    st.session_state.alpha_saved
                    * data[-1]
                    + (
                        1
                        - st.session_state.alpha_saved
                    )
                    * es_values[-1]
                )

                forecast_col1, forecast_col2 = st.columns(2)

                with forecast_col1:
                    st.metric(
                        "WMA - Próximo Período",
                        f"{next_wma:.2f}"
                    )

                with forecast_col2:
                    st.metric(
                        "ES - Próximo Período",
                        f"{next_es:.2f}"
                    )

            except Exception as e:
                st.error(
                    f"Error en el cálculo: {str(e)}"
                )