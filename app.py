import streamlit as st
from shared.sidebar import sidebar
from auth.users import get_user_by_email


LOGIN_URL = "http://localhost:5000"


def init_auth_state():
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("current_user", None)


def authenticate_user(user):
    st.session_state.authenticated = True
    st.session_state.current_user = {
        "name": user.get("name", "Usuario"),
        "email": user.get("email", ""),
        "role": user.get("role", "Analista"),
    }


def sync_auth_from_query_params():
    if st.session_state.authenticated:
        return

    access = st.query_params.get("access")
    email = st.query_params.get("email")

    if access != "demo" or not email:
        return

    user = get_user_by_email(email)
    if user:
        authenticate_user(user)
        st.query_params.clear()
        st.rerun()


def redirect_to_login():
    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url={LOGIN_URL}">
        <div style="font-family: Arial, sans-serif; padding: 2rem;">
            Redirigiendo al inicio de sesion...
            <a href="{LOGIN_URL}">Abrir login</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


st.set_page_config(
    page_title="DecisionCore DSS",
    page_icon="assets/dss_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_auth_state()
sync_auth_from_query_params()

if not st.session_state.authenticated:
    redirect_to_login()

st.title("VitalCore-DSS")
st.caption("Panel de analisis cuantitativo para soporte a decisiones empresariales.")

sidebar()
