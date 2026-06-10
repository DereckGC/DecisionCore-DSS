import streamlit as st

CURRENCY_OPTIONS = ["$", "₡", "€"]
ALPHA_PROBS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

def decision_config():

    if "currency_type" not in st.session_state:
        st.session_state.currency_type = "$"

    select_currency()

    if "alpha_hurwicz" not in st.session_state:
        st.session_state.alpha_hurwicz = 0.1

    select_alpha()


def select_currency():
    currency_selected = st.selectbox("Seleccione un tipo de moneda", CURRENCY_OPTIONS, index=0, placeholder="Elije un tipo de moneda")
    st.session_state.currency_type = currency_selected

def select_alpha():
    alpha_selected = st.select_slider("Ingrese el valor de probabilidad (Alpha)", options=ALPHA_PROBS)
    st.session_state.alpha_hurwicz = alpha_selected