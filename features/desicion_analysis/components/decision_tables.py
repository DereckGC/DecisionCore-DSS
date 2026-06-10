import streamlit as st
import pandas as pd

TABLE_STRUCTURE = {
    "Alternatives" : ["Planta Grande", "Planta Peueña", "No Hacer Nada"],
    "Mercado Favorable" : [200000, 100000, 0],
    "Mercado Desfavorable" : [-180000, -20000, 0],
}

def decision_table():

    add_new_market()
    st.divider()

    if "decision_df" not in st.session_state:
        st.session_state.decision_df = pd.DataFrame(TABLE_STRUCTURE)

    edited_df = st.data_editor(
        st.session_state.decision_df, 
        key="decision_table_editor",
        width="stretch", 
        num_rows="dynamic",
        use_container_width=True
    ) 

    st.session_state.decision_df = edited_df
    st.session_state.decision_df.set_index("Alternatives")

    market_count = len(st.session_state.decision_df.columns) - 1
    if market_count > 0:
        st.session_state.prob_markets = [1 / market_count] * market_count
    else:
        st.session_state.prob_markets = []

def add_new_market():

    col1, col2 = st.columns([3, 1])
    new_market = col1.text_input("Nuevo estado de la naturaleza")
    
    if col2.button("Añadir"):
        if new_market and new_market not in st.session_state.decision_df.columns:
            st.session_state.decision_df[new_market] = 0
            st.rerun()
