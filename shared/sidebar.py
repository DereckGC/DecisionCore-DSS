import streamlit as st
from features.desicion_analysis.desicion_analysis_view import decision_analysis

FORECAST_MODULE = "📈 Pronosticos"
DESCICION_MODULE = "⚖️ Análisis de Desición"
INVENTORY_MODULE = "📦 Inventario"
DISCOUNTS_MODULE = "🏷️ Modelo de Descuentos"

def sidebar():
    st.sidebar.header("Gestión")
    st.sidebar.image("assets/dss_icon.png")
    st.sidebar.divider()

    option = st.sidebar.radio(
        "Módulos del Sistema",
        [
            FORECAST_MODULE,
            DESCICION_MODULE,
            INVENTORY_MODULE,
            DISCOUNTS_MODULE
        ]
    )

    st.sidebar.divider()

    menu_selection(option)

def menu_selection(option):

    if(option == FORECAST_MODULE):
        #llamada al modulo
        print(f"Modulo {FORECAST_MODULE}")
    elif(option == DESCICION_MODULE):
        #llamada al modulo
        decision_analysis()
    elif(option == INVENTORY_MODULE):
        #llamada al modulo
        print(f"Modulo {FORECAST_MODULE}")
    elif(option == DISCOUNTS_MODULE):
        #llamada al modulo
        print(f"Modulo {FORECAST_MODULE}")