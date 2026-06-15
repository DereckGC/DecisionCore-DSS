import streamlit as st
import pandas as pd

def calculate_poe(decision_df):
    df_loss = calculate_loss_by_market(decision_df)

    poe_max = df_loss.max(axis=1)

    best_value = poe_max.min()
    best_alternatives = poe_max[poe_max == best_value].index.tolist()

    return {
        "poe_results": poe_max,
        "best_value": best_value,
        "best_alternatives": best_alternatives,
        "loss_matrix": df_loss
    }

def calculate_loss_by_market(decision_df):
    df_calc = decision_df.set_index("Alternatives")
    df_calc = df_calc.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_losses = df_calc.max(axis=0) - df_calc
    return df_losses
