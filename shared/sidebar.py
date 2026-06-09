import streamlit as st

FORECAST_MODULE = "📈 Forecast"
DESCICION_MODULE = "⚖️ Desicion Tables"
INVENTORY_MODULE = "📦 Inventory"
DISCOUNTS_MODULE = "🏷️ Discounts"

def sidebar():
    st.sidebar.header("Management")
    st.sidebar.image("assets\dss_icon.png")
    st.sidebar.divider()

    option = st.sidebar.radio(
        "System Modules",
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
        print(f"Modulo {DESCICION_MODULE}")

    elif(option == INVENTORY_MODULE):
        #llamada al modulo
        print(f"Modulo {INVENTORY_MODULE}")

    elif(option == DISCOUNTS_MODULE):
        #llamada al modulo
        print(f"Modulo {DISCOUNTS_MODULE}")