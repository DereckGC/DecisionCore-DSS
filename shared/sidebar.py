import streamlit as st

from features.desicion_analysis.desicion_analysis_view import decision_analysis


FORECAST_MODULE = "Pronosticos"
DECISION_MODULE = "Analisis de Decision"
INVENTORY_MODULE = "Inventario"
DISCOUNTS_MODULE = "Modelo de Descuentos"


def sidebar():
    current_user = st.session_state.get("current_user", {})
    user_name = current_user.get("name", "Usuario")
    user_role = current_user.get("role", "Analista")

    st.sidebar.header("Gestion")
    st.sidebar.image("assets/dss_icon.png")
    st.sidebar.markdown(f"**{user_name}**")
    st.sidebar.caption(user_role)

    if st.sidebar.button("Cerrar sesion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()
    st.sidebar.divider()

    option = st.sidebar.radio(
        "Modulos del Sistema",
        [
            FORECAST_MODULE,
            DECISION_MODULE,
            INVENTORY_MODULE,
            DISCOUNTS_MODULE,
        ],
    )

    st.sidebar.divider()

    menu_selection(option)


def menu_selection(option):
    if option == FORECAST_MODULE:
        st.info("Modulo de pronosticos en preparacion.")
    elif option == DECISION_MODULE:
        decision_analysis()
    elif option == INVENTORY_MODULE:
        st.info("Modulo de inventario en preparacion.")
    elif option == DISCOUNTS_MODULE:
        st.info("Modulo de descuentos en preparacion.")
