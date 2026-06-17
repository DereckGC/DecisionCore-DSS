import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math

from features.discount_analysis.logic.cle import calcular_descuento_cantidad
from features.discount_analysis.components.discounts_table import render_discounts_table
from features.discount_analysis.components.monte_carlo_simulation import render_montecarlo_descuento

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
    

    render_montecarlo_descuento(
        D, Co, holding_value, is_percentage,
        precio_optimo, Q_optimo,
        costo_total_minimo, nivel_optimo
    )