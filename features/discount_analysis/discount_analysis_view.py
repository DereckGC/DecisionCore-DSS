import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math

from features.discount_analysis.logic.cle import calcular_descuento_cantidad
from features.discount_analysis.components.discounts_table import render_discounts_table

def discount_analysis_view():
    st.subheader("Modelos de Inventarios: Descuentos por Cantidad")
    

    st.markdown("""
    <style>
    .result-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        border: 1px solid #2a2d3a;
        margin-bottom: 15px;
    }
    .result-card h4 {
        color: #7b808e;
        font-size: 10px;
        margin-bottom: 8px;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 600;
    }
    .result-card h3 {
        color: #e5e7eb;
        font-size: 13px;
        margin-bottom: 6px;
        margin-top: 0;
        font-weight: 500;
    }
    .result-card h2 {
        color: #4f80ff;
        font-size: 22px;
        margin: 0;
        font-weight: bold;
    }
    .result-card.winner {
        border-color: #4ade80;
        background-color: #142a1e;
    }
    .result-card.winner h2 {
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
    .explanation-box {
        background-color: #1e2029;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        font-size: 13.5px;
        color: #d1d5db;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
    
   
    st.markdown('<div class="section-title">1. Parámetros de Entrada y Tabla de Descuentos</div>', unsafe_allow_html=True)
    
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
            D = col1.number_input("Demanda Anual (D)", min_value=0.0, value=None, placeholder="Ingrese la demanda anual (D)", format="%.2f")
    else:
        D = col1.number_input("Demanda Anual (D)", min_value=0.0, value=None, placeholder="Ingrese la demanda anual (D)", format="%.2f")
        
    Co = col2.number_input("Costo por Ordenar (Co)", min_value=0.0, value=None, placeholder="Ingrese el costo por ordenar (Co)", format="%.2f")
    
    col3, col4 = st.columns(2)
    holding_type = col3.selectbox(
        "Costo de Almacenamiento",
        ["Tasa de almacenamiento (I) [% del precio]", "Costo fijo unitario anual (Ch)"]
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
        holding_value = col4.number_input("Costo fijo anual por almacenar (Ch)", min_value=0.0, value=None, placeholder="Ingrese costo de almacenamiento (Ch)", format="%.2f")
        
    
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
        
    
    discount_rows = []
    for idx, r in st.session_state.discount_df.iterrows():
        discount_rows.append({
            "min_qty": r["Cantidad Mínima"],
            "price": r["Precio Unitario"]
        })
        
   
    res = calcular_descuento_cantidad(D, Co, holding_value, is_percentage, discount_rows)
    
    if res.get("error"):
        st.error(res["error"])
        return
        
    Q_optimo = res["Q_optimo"]
    nivel_optimo = res["nivel_optimo"]
    precio_optimo = res["precio_optimo"]
    costo_total_minimo = res["costo_total_minimo"]
    desglose = res["desglose"]
    df_comparativo = res["tabla_comparativa"]
    

    st.markdown('<div class="section-title">2. Resultados del Modelo (Cantidad Óptima Q*)</div>', unsafe_allow_html=True)
    
   
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    with col_kpi1:
        st.markdown(f"""
        <div class="result-card winner">
            <h4>Cantidad Óptima (Q*)</h4>
            <h2>{Q_optimo:,.0f}</h2>
            <h3>unidades / orden</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi2:
        st.markdown(f"""
        <div class="result-card winner">
            <h4>Costo Total Mínimo</h4>
            <h2>${costo_total_minimo:,.2f}</h2>
            <h3>anual proyectado</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi3:
        st.markdown(f"""
        <div class="result-card">
            <h4>Precio Unitario</h4>
            <h2>${precio_optimo:,.2f}</h2>
            <h3>Nivel {nivel_optimo}</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_kpi4:
        st.markdown(f"""
        <div class="result-card">
            <h4>Frecuencia de Pedidos</h4>
            <h2>{D/Q_optimo:,.1f}</h2>
            <h3>órdenes al año</h3>
        </div>
        """, unsafe_allow_html=True)
        
 
    st.markdown("#### Desglose de Niveles y Costos Comparados")
    
    def highlight_row(row):
        is_winner = row["Nivel"] == nivel_optimo
        return ["background-color: #142a1e; color: #4ade80; font-weight: bold;" if is_winner else "" for _ in row]
        
    styled_df = df_comparativo.style.apply(highlight_row, axis=1).format({
        "Precio ($)": "${:,.2f}",
        "Q* Teórico": "{:,.2f}",
        "Q Real": "{:,.0f}",
        "Costo Material": "${:,.2f}",
        "Costo Ordenar": "${:,.2f}",
        "Costo Almacenar": "${:,.2f}",
        "Costo Total": "${:,.2f}"
    })
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
   
    st.markdown('<div class="section-title">3. Simulación de Riesgo de Demanda (Monte Carlo)</div>', unsafe_allow_html=True)
    st.write(f"Manteniendo la decisión fija de ordenar **Q* = {Q_optimo:,.0f}** a un precio de **\${precio_optimo:.2f}**, simulamos qué ocurre con el costo si la demanda anual cambia.")
    
    col_mc1, col_mc2 = st.columns(2)
    n_sim = col_mc1.slider("Número de Simulaciones", min_value=1000, max_value=10000, value=10000, step=1000)
    dist_type = col_mc2.selectbox("Distribución de la Demanda", ["Normal (Incertidumbre)", "Uniforme (Rango Equitativo)"])
    
    col_mc3, col_mc4 = st.columns(2)
    if dist_type == "Normal (Incertidumbre)":
        cv = col_mc3.slider("Coeficiente de Variación (Volatilidad de demanda)", min_value=0.05, max_value=0.30, value=0.15, step=0.05)
        std_dev = D * cv
        st.caption(f"Desviación estándar calculada: **{std_dev:,.2f}** unidades.")
        range_pct = 0.0
    else:
        range_pct = col_mc3.slider("Rango de Variación (±%) alrededor de la demanda", min_value=10, max_value=50, value=20, step=5) / 100
        std_dev = 0.0
        
    if st.button("▶ Ejecutar Simulación de Riesgo", use_container_width=True):
        np.random.seed(42)
        if dist_type == "Normal (Incertidumbre)":
            demands_sim = np.random.normal(D, std_dev, n_sim)
        else:
            demands_sim = np.random.uniform(D * (1 - range_pct), D * (1 + range_pct), n_sim)
            
        demands_sim = np.clip(demands_sim, 1, None)
        
        Ch_opt = holding_value * precio_optimo if is_percentage else holding_value
        costs_sim = demands_sim * precio_optimo + (demands_sim / Q_optimo) * Co + (Q_optimo / 2) * Ch_opt
        
        mean_c = np.mean(costs_sim)
        std_c = np.std(costs_sim)
        min_c = np.min(costs_sim)
        max_c = np.max(costs_sim)
        p10 = np.percentile(costs_sim, 10)
        median_c = np.percentile(costs_sim, 50)
        p90 = np.percentile(costs_sim, 90)
        
        risk_pct = (costs_sim > costo_total_minimo).mean() * 100
        
      
        col_rkpi1, col_rkpi2, col_rkpi3 = st.columns(3)
        with col_rkpi1:
            st.metric("Costo Promedio Simulado", f"${mean_c:,.2f}")
        with col_rkpi2:
            st.metric("Desviación Estándar", f"${std_c:,.2f}")
        with col_rkpi3:
            st.metric("Riesgo de Exceder Presupuesto", f"{risk_pct:.1f}%")
            
    
        st.markdown("#### Estadísticas de Riesgo")
        stat_df = pd.DataFrame({
            "Métrica / Percentil": ["Mínimo", "Percentil 10%", "Mediana (P50)", "Percentil 90%", "Máximo"],
            "Costo Total Simulado": [min_c, p10, median_c, p90, max_c]
        })
        st.dataframe(stat_df.style.format({"Costo Total Simulado": "${:,.2f}"}), use_container_width=True, hide_index=True)
        
        
        col_gs1, col_gs2 = st.columns(2)
        
        with col_gs1:
            fig_hist = px.histogram(
                x=costs_sim,
                nbins=40,
                color_discrete_sequence=["#3b82f6"],
                title="Frecuencia de Costo Total Simulado"
            )
            fig_hist.add_vline(x=costo_total_minimo, line_dash="dash", line_color="#ef4444", line_width=2, annotation_text="Costo Determinista")
            fig_hist.update_layout(
                xaxis_title="Costo Total Anual ($)",
                yaxis_title="Casos",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb")
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_gs2:
            sorted_costs = np.sort(costs_sim)
            cdf = np.arange(1, len(sorted_costs) + 1) / len(sorted_costs)
            
            fig_cdf = go.Figure()
            fig_cdf.add_trace(go.Scatter(
                x=sorted_costs,
                y=cdf * 100,
                mode='lines',
                line=dict(color='#10b981', width=3),
                name="Prob. Acumulada"
            ))
            fig_cdf.add_vline(x=costo_total_minimo, line_dash="dash", line_color="#ef4444", line_width=2, annotation_text="Presupuesto")
            fig_cdf.update_layout(
                title="Curva S de Probabilidad Acumulada",
                xaxis_title="Costo Total Anual ($)",
                yaxis_title="Probabilidad Acumulada (%)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb")
            )
            fig_cdf.update_xaxes(showgrid=True, gridcolor="#2a2d3a")
            fig_cdf.update_yaxes(showgrid=True, gridcolor="#2a2d3a")
            st.plotly_chart(fig_cdf, use_container_width=True)
            
        st.info(f"💡 Comprar lotes de **{Q_optimo:,.0f}** unidades al precio de **\${precio_optimo:.2f}** resulta en un costo promedio estimado de **\${mean_c:,.2f}**. Debido a la variabilidad aleatoria de la demanda, existe un **{risk_pct:.1f}%** de riesgo de que el costo real sea mayor que el presupuesto de **\${costo_total_minimo:,.2f}**.")