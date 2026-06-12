import streamlit as st
import pandas as pd

def calculate_vme(decision_df, probs):

    df_calc = decision_df.set_index("Alternatives")
    df_calc = df_calc.apply(pd.to_numeric, errors='coerce').fillna(0)

    df_weighted = df_calc.multiply(probs, axis=1)

    vme_sums = df_weighted.sum(axis=1)

    best_value = vme_sums.max()
    best_alternatives = vme_sums[vme_sums == best_value].index.tolist()

    vme_results = []
    for alt in df_calc.index:
        vme_results.append({
            "Alternatives": alt,
            "VME": vme_sums[alt],
            "Weighted_Values": df_weighted.loc[alt].to_dict()
        })

    return {
        "vme_results": vme_results,
        "best_value": best_value,
        "best_alternatives": best_alternatives
    }
