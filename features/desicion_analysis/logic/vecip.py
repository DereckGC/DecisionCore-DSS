import streamlit as st
import pandas as pd

def calculate_vecip(maximax_results, minimax_results, prob_markets):
    if "decision_df" not in st.session_state or st.session_state.decision_df is None or st.session_state.decision_df.empty:
        return None

    decision_df = st.session_state.decision_df.set_index("Alternatives")
    decision_df = decision_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    best_by_market = decision_df.max(axis=0)

    vecip = best_by_market.multiply(prob_markets, axis=0).sum()

    return vecip
