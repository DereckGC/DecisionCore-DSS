import streamlit as st
import matplotlib.pyplot as plt

def display_comparison(data, methods_data, metrics_df):

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Comparación de Métodos")

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            data,
            'ko-',
            label='Datos Reales',
            linewidth=2,
            markersize=6
        )

        ax.plot(
            methods_data['WMA'],
            'b--',
            label='WMA',
            alpha=0.7,
            linewidth=2
        )

        ax.plot(
            methods_data['ES'],
            'r--',
            label='Suavizamiento Exponencial',
            alpha=0.7,
            linewidth=2
        )

        ax.set_xlabel('Período', fontsize=12)
        ax.set_ylabel('Valor', fontsize=12)

        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        st.pyplot(fig)

    with col2:
        st.subheader("Métricas")

        st.dataframe(
            metrics_df.round(4),
            use_container_width=True
        )

        best_method = metrics_df.loc[
            metrics_df['DMA'].idxmin(),
            'Método'
        ]

        best_dma = metrics_df.loc[
            metrics_df['DMA'].idxmin(),
            'DMA'
        ]

        st.success(
            f"Mejor: **{best_method}** (DMA: {best_dma:.4f})"
        )