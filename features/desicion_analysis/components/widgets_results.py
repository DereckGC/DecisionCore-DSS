import streamlit as st
import pandas as pd

def render_results_widgets(results_dict):

    st.markdown("""
    <style>
    .results-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .grid-row {
        display: flex;
        gap: 15px;
        margin-bottom: 15px;
    }
    .result-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        border: 1px solid #2a2d3a;
        flex: 1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .result-card h4 {
        color: #7b808e;
        font-size: 11px;
        margin-bottom: 8px;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    .result-card h3 {
        color: #e5e7eb;
        font-size: 15px;
        margin-bottom: 8px;
        margin-top: 0;
        font-weight: 500;
    }
    .result-card h2 {
        color: #4f80ff;
        font-size: 22px;
        margin: 0;
        font-weight: bold;
    }
    .section-title {
        color: #e5e7eb;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        border-left: 4px solid #4f80ff;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    currency = st.session_state.get("currency_type", "$")

    def format_val(val):
        if val is None or pd.isna(val):
            return "—"
        return f"{currency}{val:,.0f}"

    def format_alt(alts):
        if not alts:
            return "—"
        if isinstance(alts, list):
            return " / ".join([str(a) for a in alts])
        return str(alts)

    def highlight_vme_poe(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)

        if "VME" in df.columns:
            vme_values = pd.to_numeric(df["VME"], errors="coerce")
            styles.loc[vme_values == vme_values.max(), "VME"] = (
                "background-color: #14532d; color: #dcfce7; font-weight: 700;"
            )

        if "POE" in df.columns:
            poe_values = pd.to_numeric(df["POE"], errors="coerce")
            styles.loc[poe_values == poe_values.min(), "POE"] = (
                "background-color: #14532d; color: #dcfce7; font-weight: 700;"
            )
            styles.loc[poe_values == poe_values.max(), "POE"] = (
                "background-color: #7f1d1d; color: #fee2e2; font-weight: 700;"
            )

        return styles

    m_max = results_dict.get("maximax", {})
    m_min = results_dict.get("minimax", {})
    m_hurwicz = results_dict.get("hurwicz", {})
    m_vme = results_dict.get("vme", {})
    m_laplace = results_dict.get("laplace", {})
    m_poe = results_dict.get("poe", {})
    veip = results_dict.get("veip", None)
    vecip = results_dict.get("vecip", None)

    alpha = st.session_state.get("alpha_hurwicz", 0.5)

    st.markdown('<div class="section-title">Resultados por criterio</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="result-card">
            <h4>MAXIMAX</h4>
            <h3>{format_alt(m_max.get('best_alternatives'))}</h3>
            <h2>{format_val(m_max.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="result-card">
            <h4>MAXIMIN</h4>
            <h3>{format_alt(m_min.get('best_alternatives'))}</h3>
            <h2>{format_val(m_min.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="result-card">
            <h4>HURWICZ A={alpha}</h4>
            <h3>{format_alt(m_hurwicz.get('best_alternatives'))}</h3>
            <h2>{format_val(m_hurwicz.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="result-card">
            <h4>VME</h4>
            <h3>{format_alt(m_vme.get('best_alternatives'))}</h3>
            <h2>{format_val(m_vme.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
        <div class="result-card">
            <h4>PROB. IGUALES</h4>
            <h3>{format_alt(m_laplace.get('best_alternatives'))}</h3>
            <h2>{format_val(m_laplace.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="result-card">
            <h4>POE</h4>
            <h3>{format_alt(m_poe.get('best_alternatives'))}</h3>
            <h2>{format_val(m_poe.get('best_value'))}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
        <div class="result-card">
            <h4>VEIP</h4>
            <h3>—</h3>
            <h2>{format_val(veip)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
        <div class="result-card">
            <h4>VECIP</h4>
            <h3>—</h3>
            <h2>{format_val(vecip)}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Matriz de pagos y criterios</div>', unsafe_allow_html=True)

    if "decision_df" in st.session_state and not st.session_state.decision_df.empty:
        df_view = st.session_state.decision_df.copy()
        df_view = df_view.set_index("Alternatives")

        if "vme_results" in m_vme:
            vmes = {res["Alternatives"]: res["VME"] for res in m_vme["vme_results"]}
            df_view["VME"] = df_view.index.map(vmes)

        if "poe_results" in m_poe:
            poes = m_poe["poe_results"]
            df_view["POE"] = df_view.index.map(poes)

        if "resultados" in m_max:
            maxs = {res["Alternatives"]: res["Valor"] for res in m_max["resultados"]}
            df_view["MAX"] = df_view.index.map(maxs)

        if "resultados" in m_min:
            mins = {res["Alternatives"]: res["Valor"] for res in m_min["resultados"]}
            df_view["MIN"] = df_view.index.map(mins)

        styled_df = df_view.style.format(f"{currency}{{:.0f}}").apply(highlight_vme_poe, axis=None)

        st.dataframe(
            styled_df,
            use_container_width=True
        )