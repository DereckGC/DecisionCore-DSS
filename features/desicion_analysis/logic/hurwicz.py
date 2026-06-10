import streamlit as st
import pandas as pd

def calculate_hurwicz(decision_df, alpha):
  
    decision_df = decision_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    max_per_alt = decision_df.max(axis=1)
    min_per_alt = decision_df.min(axis=1)

    df_hurwicz = (alpha * max_per_alt) + ((1 - alpha) * min_per_alt)

    best_value = df_hurwicz.max()
    best_alternatives = df_hurwicz[df_hurwicz == best_value].index.tolist()

    return {
        "hurwicz_results": df_hurwicz,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
