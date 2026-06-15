import streamlit as st
import pandas as pd

TABLE_STRUCTURE = {
    "Alternatives": [
        "Capacidad Base (1 Turno)", 
        "Expansión Modular (2 Turnos + Automatización)", 
        "Planta de Alta Intensidad (Turnos 24/7)"
    ],
    "Demanda Alta": [50000, 250000, 450000],
    "Demanda Moderada": [150000, 200000, 50000],
    "Demanda Baja": [100000, -50000, -300000],
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
        # Solo inicializa si no existe o si el número de mercados cambió
        current = st.session_state.get("prob_markets", [])
        if len(current) != market_count:
            st.session_state.prob_markets = [round(1 / market_count, 4)] * market_count
    else:
        st.session_state.prob_markets = []

def render_probability_inputs():
    markets = [col for col in st.session_state.decision_df.columns if col != "Alternatives"]
    probs = st.session_state.get("prob_markets", [])

    if not markets:
        return

    st.markdown("**Probabilidades por estado de la naturaleza**")
    cols = st.columns(len(markets))

    new_probs = []
    for i, (market, col) in enumerate(zip(markets, cols)):
        current_val = probs[i] if i < len(probs) else round(1 / len(markets), 4)
        val = col.number_input(
            label=market,
            min_value=0.0,
            max_value=1.0,
            value=float(current_val),
            step=0.01,
            format="%.2f",
            key=f"prob_input_{market}"
        )
        new_probs.append(val)

    total = round(sum(new_probs), 4)
    st.session_state.prob_markets = new_probs

    if abs(total - 1.0) > 0.001:
        st.warning(f"Las probabilidades suman {total:.2f}. Deben sumar 1.00")
    else:
        st.success(f"Probabilidades válidas ✓ (suma = {total:.2f})")

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

    st.divider()
    render_probability_inputs()

def add_new_market():
    col1, col2 = st.columns([3, 1])
    new_market = col1.text_input("Nuevo estado de la naturaleza")

    if col2.button("Añadir"):
        if new_market and new_market not in st.session_state.decision_df.columns:
            st.session_state.decision_df[new_market] = 0
            _recalculate_probabilities()
            st.rerun()