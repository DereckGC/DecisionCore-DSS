import streamlit as st
import pandas as pd

def calculate_maximax(decision_df):

    df_maximax = decision_df.max(axis=1, numeric_only=True)
    best_value = df_maximax.max()
    best_alternatives = df_maximax[df_maximax == best_value].index.tolist()

    return {
        "maximax_results": df_maximax,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
