import streamlit as st
import pandas as pd

def calculate_minimax(decision_df):
    
    df = decision_df.set_index("Alternatives") 
    
    df_minimax = df.min(axis=1, numeric_only=True)
    best_value = df_minimax.max()
    best_alternatives = df_minimax[df_minimax == best_value].index.tolist()

    return {
        "minimax_results": df_minimax,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }