import streamlit as st
import pandas as pd

def calculate_maximax(decision_df):

    df = decision_df.set_index("Alternatives")  
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0) 
    
    df_maximax = df.max(axis=1)
    best_value = df_maximax.max()
    best_alternatives = df_maximax[df_maximax == best_value].index.tolist()

    return {
        "maximax_results": df_maximax,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
