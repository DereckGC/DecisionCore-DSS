import streamlit as st
import pandas as pd

def calculate_laplace(decision_df):

    df = decision_df.set_index("Alternatives")  
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    df_laplace = df.mean(axis=1)
    
    best_value = df_laplace.max()
    best_alternatives = df_laplace[df_laplace == best_value].index.tolist()

    return {
        "laplace_results": df_laplace,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
