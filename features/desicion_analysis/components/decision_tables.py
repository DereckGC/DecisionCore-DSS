import streamlit as st
import pandas as pd

TABLE_STRUCTURE = {
    "Alternatives": ["Planta Grande", "Planta Pequeña", "No Hacer Nada"],
    "Mercado Favorable": [200000, 100000, 0],
    "Mercado Desfavorable": [-180000, -20000, 0],
}

def on_table_change():
    editor_state = st.session_state.decision_table_editor

    updated_df = st.session_state.decision_df.copy()

    for idx, changes in editor_state.get("edited_rows", {}).items():
        for col, val in changes.items():
            updated_df.at[idx, col] = val

    for row in editor_state.get("added_rows", []):
        new_row = {col: row.get(col, None) for col in updated_df.columns}
        updated_df = pd.concat([updated_df, pd.DataFrame([new_row])], ignore_index=True)

    deleted = editor_state.get("deleted_rows", [])
    if deleted:
        updated_df = updated_df.drop(index=deleted).reset_index(drop=True)

    st.session_state.decision_df = updated_df
    _recalculate_probabilities()

def _recalculate_probabilities():
    market_count = len(st.session_state.decision_df.columns) - 1
    if market_count > 0:
        st.session_state.prob_markets = [1 / market_count] * market_count
    else:
        st.session_state.prob_markets = []

def decision_table():
    if "decision_df" not in st.session_state:
        st.session_state.decision_df = pd.DataFrame(TABLE_STRUCTURE)
    if "prob_markets" not in st.session_state:
        _recalculate_probabilities()

    add_new_market()
    st.divider()

    st.data_editor(
        st.session_state.decision_df,
        key="decision_table_editor",
        on_change=on_table_change,   
        num_rows="dynamic",
        use_container_width=True,
    )

def add_new_market():
    col1, col2 = st.columns([3, 1])
    new_market = col1.text_input("Nuevo estado de la naturaleza")

    if col2.button("Añadir"):
        if new_market and new_market not in st.session_state.decision_df.columns:
            st.session_state.decision_df[new_market] = 0
            _recalculate_probabilities()
            st.rerun()