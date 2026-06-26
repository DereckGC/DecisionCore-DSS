import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def display_comparison(data, methods_data, metrics_df):

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Comparación de Métodos")

        fig = go.Figure()

        # Datos reales
        fig.add_trace(go.Scatter(
            y=data,
            mode="lines+markers",
            name="Datos Reales",
            line=dict(color="#e5e7eb", width=3),
            marker=dict(size=6)
        ))

        # WMA
        fig.add_trace(go.Scatter(
            y=methods_data["WMA"],
            mode="lines",
            name="WMA",
            line=dict(color="#4f80ff", width=3)
        ))

        # ES
        fig.add_trace(go.Scatter(
            y=methods_data["ES"],
            mode="lines",
            name="Suavizamiento Exponencial",
            line=dict(color="#f97316", width=3)
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1a1c24",
            plot_bgcolor="#1a1c24",
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            ),
            xaxis_title="Período",
            yaxis_title="Valor"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Métricas")

        st.dataframe(
            metrics_df.round(4),
            use_container_width=True
        )

        best_method = metrics_df.loc[
            metrics_df["DMA"].idxmin(),
            "Método"
        ]

        best_dma = metrics_df.loc[
            metrics_df["DMA"].idxmin(),
            "DMA"
        ]

        st.success(
            f"Mejor modelo: **{best_method}** (DMA: {best_dma:.4f})"
        )