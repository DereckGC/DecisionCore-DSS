import streamlit as st
import pandas as pd

def calculate_laplace(decision_df):

    decision_df = decision_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    df_laplace = decision_df.mean(axis=1)
    
    best_value = df_laplace.max()
    best_alternatives = df_laplace[df_laplace == best_value].index.tolist()

    return {
        "laplace_results": df_laplace,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
