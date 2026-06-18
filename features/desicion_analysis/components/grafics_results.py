import pandas as pd
import streamlit as st


def render_results_charts(results_dict):
    currency = st.session_state.get("currency_type", "$")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Graficos de resultados</div>',
        unsafe_allow_html=True
    )

    criteria_df = build_criteria_df(results_dict)
    vme_df = build_vme_df(results_dict)
    poe_df = build_poe_df(results_dict)
    payoff_df = build_payoff_df()

    tab1, tab2 = st.tabs(["Criterios", "VME y POE"])

    with tab1:
        if not criteria_df.empty:
            st.bar_chart(criteria_df["Valor"], use_container_width=True)
            st.dataframe(
                criteria_df.style.format({"Valor": f"{currency}{{:,.0f}}"}),
                use_container_width=True
            )

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            if not vme_df.empty:
                st.markdown("**VME por alternativa**")
                st.bar_chart(vme_df["VME"], use_container_width=True)

        with col2:
            if not poe_df.empty:
                st.markdown("**POE por alternativa**")
                st.bar_chart(poe_df["POE"], use_container_width=True)



def build_criteria_df(results_dict):
    criteria = {
        "Maximax": get_best_value(results_dict, "maximax"),
        "Maximin": get_best_value(results_dict, "minimax"),
        "Hurwicz": get_best_value(results_dict, "hurwicz"),
        "Laplace": get_best_value(results_dict, "laplace"),
        "VME": get_best_value(results_dict, "vme"),
        "POE": get_best_value(results_dict, "poe"),
        "VEIP": results_dict.get("veip"),
        "VECIP": results_dict.get("vecip"),
    }

    criteria_df = pd.DataFrame(
        [{"Criterio": name, "Valor": value} for name, value in criteria.items()]
    )
    criteria_df["Valor"] = pd.to_numeric(criteria_df["Valor"], errors="coerce")

    return criteria_df.dropna(subset=["Valor"]).set_index("Criterio")


def build_vme_df(results_dict):
    vme_results = results_dict.get("vme", {}).get("vme_results", [])
    if not vme_results:
        return pd.DataFrame()

    vme_df = pd.DataFrame(vme_results)
    vme_df["VME"] = pd.to_numeric(vme_df["VME"], errors="coerce")

    return vme_df[["Alternatives", "VME"]].dropna().set_index("Alternatives")


def build_poe_df(results_dict):
    poe_results = results_dict.get("poe", {}).get("poe_results")
    if poe_results is None:
        return pd.DataFrame()

    poe_df = poe_results.rename("POE").to_frame()
    poe_df["POE"] = pd.to_numeric(poe_df["POE"], errors="coerce")

    return poe_df.dropna()


def build_payoff_df():
    if "decision_df" not in st.session_state or st.session_state.decision_df.empty:
        return pd.DataFrame()

    payoff_df = st.session_state.decision_df.set_index("Alternatives")
    return payoff_df.apply(pd.to_numeric, errors="coerce").fillna(0)


def get_best_value(results_dict, key):
    result = results_dict.get(key, {})
    if isinstance(result, dict):
        return result.get("best_value")
    return None
