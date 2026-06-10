import streamlit as st
import pandas as pd

def calculate_poe(decision_df):
    
    df_loss = calculate_loss_by_market(decision_df)

    prob_markets = st.session_state.get("prob_markets", [])
    if len(prob_markets) != len(df_loss.columns):
        prob_markets = [1 / len(df_loss.columns)] * len(df_loss.columns)

    df_weighted_losses = df_loss.multiply(prob_markets, axis=1)
    
    poe_sums = df_weighted_losses.sum(axis=1)

    best_value = poe_sums.min()
    best_alternatives = poe_sums[poe_sums == best_value].index.tolist()

    return {
        "poe_results": poe_sums,
        "best_value": best_value,
        "best_alternatives": best_alternatives,
        "loss_matrix": df_loss 
    }

def calculate_loss_by_market(decision_df):
    df_calc = decision_df.set_index("Alternatives")
    df_calc = df_calc.apply(pd.to_numeric, errors='coerce').fillna(0)

    df_max_value_by_market = df_calc.max(axis=0)

    df_losses = df_max_value_by_market - df_calc

    return df_losses
