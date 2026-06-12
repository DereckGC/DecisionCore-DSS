import streamlit as st
import pandas as pd


def render_results_widgets(results_dict):

    st.markdown("""
    <style>
    .result-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        border: 1px solid #2a2d3a;
        flex: 1;
        margin-bottom: 10px;
        position: relative;
    }
    .result-card h4 {
        color: #7b808e;
        font-size: 10px;
        margin-bottom: 10px;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 600;
    }
    .result-card h3 {
        color: #e5e7eb;
        font-size: 13px;
        margin-bottom: 6px;
        margin-top: 0;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .result-card h2 {
        color: #4f80ff;
        font-size: 20px;
        margin: 0;
        font-weight: bold;
    }
    .result-card.winner {
        border-color: #4f80ff;
        background-color: #1a2035;
    }
    .badge {
        display: inline-block;
        font-size: 9px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 2px 8px;
        border-radius: 20px;
        margin-bottom: 8px;
    }
    .badge-optimista { background: #1e3a5f; color: #60a5fa; }
    .badge-pesimista { background: #1f2937; color: #9ca3af; }
    .badge-riesgo    { background: #1e3a2f; color: #4ade80; }
    .badge-info      { background: #2d1f3d; color: #c084fc; }
    .section-title {
        color: #e5e7eb;
        font-size: 16px;
        font-weight: bold;
        margin: 24px 0 12px;
        border-left: 4px solid #4f80ff;
        padding-left: 10px;
    }
    .divider-label {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0 12px;
    }
    .divider-label span {
        color: #7b808e;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        white-space: nowrap;
    }
    .divider-label hr {
        flex: 1;
        border: none;
        border-top: 1px solid #2a2d3a;
        margin: 0;
    }
    .insight-box {
        background: #1a2035;
        border: 1px solid #2a3a5a;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 16px;
    }
    .insight-box p {
        margin: 0;
        font-size: 13px;
        color: #9ca3af;
        line-height: 1.6;
    }
    .insight-box strong {
        color: #e5e7eb;
    }
    </style>
    """, unsafe_allow_html=True)

    currency = st.session_state.get("currency_type", "$")
    alpha    = st.session_state.get("alpha_hurwicz", 0.5)

    def fmt(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "—"
        return f"{currency}{val:,.0f}"

    def fmt_alt(alts):
        if not alts:
            return "—"
        if isinstance(alts, list):
            return " / ".join(str(a) for a in alts)
        return str(alts)

    m_max     = results_dict.get("maximax", {})
    m_min     = results_dict.get("minimax", {})
    m_hurwicz = results_dict.get("hurwicz", {})
    m_vme     = results_dict.get("vme", {})
    m_laplace = results_dict.get("laplace", {})
    m_poe     = results_dict.get("poe", {})
    veip      = results_dict.get("veip", None)
    vecip     = results_dict.get("vecip", None)

    def card(badge_class, badge_label, title, alt, val):
        return f"""
        <div class="result-card">
            <span class="badge {badge_class}">{badge_label}</span>
            <h4>{title}</h4>
            <h3>{alt}</h3>
            <h2>{val}</h2>
        </div>"""

    st.markdown('<div class="section-title">Resultados por criterio</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider-label"><span>Sin probabilidades</span><hr></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(card(
            "badge-optimista", "Optimista",
            "Maximax",
            fmt_alt(m_max.get("best_alternatives")),
            fmt(m_max.get("best_value"))
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(card(
            "badge-pesimista", "Pesimista",
            "Maximin",
            fmt_alt(m_min.get("best_alternatives")),
            fmt(m_min.get("best_value"))
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(card(
            "badge-info", f"Alpha = {alpha}",
            "Hurwicz",
            fmt_alt(m_hurwicz.get("best_alternatives")),
            fmt(m_hurwicz.get("best_value"))
        ), unsafe_allow_html=True)

    st.markdown('<div class="divider-label"><span>Con probabilidades</span><hr></div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(card(
            "badge-riesgo", "Probabilidades iguales",
            "Laplace",
            fmt_alt(m_laplace.get("best_alternatives")),
            fmt(m_laplace.get("best_value"))
        ), unsafe_allow_html=True)
    with c5:
        st.markdown(card(
            "badge-riesgo", "Valor monetario esperado",
            "VME",
            fmt_alt(m_vme.get("best_alternatives")),
            fmt(m_vme.get("best_value"))
        ), unsafe_allow_html=True)
    with c6:
        st.markdown(card(
            "badge-pesimista", "Minimax arrepentimiento",
            "POE",
            fmt_alt(m_poe.get("best_alternatives")),
            fmt(m_poe.get("best_value"))
        ), unsafe_allow_html=True)

    st.markdown('<div class="divider-label"><span>Valor de la información</span><hr></div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        st.markdown(f"""
        <div class="result-card">
            <span class="badge badge-info">Información perfecta</span>
            <h4>VECIP</h4>
            <h3>Valor esperado con info completa</h3>
            <h2>{fmt(vecip)}</h2>
        </div>""", unsafe_allow_html=True)
    with c8:
        st.markdown(f"""
        <div class="result-card">
            <span class="badge badge-info">Ganancia máxima</span>
            <h4>VEIP</h4>
            <h3>Lo que pagarías por información perfecta</h3>
            <h2>{fmt(veip)}</h2>
        </div>""", unsafe_allow_html=True)

    _render_insight_box(m_max, m_min, m_vme, m_poe, veip, currency)

    st.markdown('<div class="section-title">Matriz de pagos y criterios</div>', unsafe_allow_html=True)
    _render_matrix(results_dict, currency)


def _render_insight_box(m_max, m_min, m_vme, m_poe, veip, currency):
    best_vme = m_vme.get("best_alternatives", [])
    best_max = m_max.get("best_alternatives", [])
    best_poe = m_poe.get("best_alternatives", [])

    coincide_vme_max = set(best_vme) & set(best_max)
    coincide_vme_poe = set(best_vme) & set(best_poe)

    lines = []

    if coincide_vme_max:
        lines.append(f"<strong>{', '.join(coincide_vme_max)}</strong> lidera tanto en Maximax como en VME, lo que sugiere una alternativa dominante.")
    elif best_vme:
        lines.append(f"El VME favorece <strong>{', '.join(best_vme)}</strong>, pero no coincide con el Maximax, indicando un trade-off entre optimismo y rentabilidad esperada.")

    if coincide_vme_poe:
        lines.append(f"<strong>{', '.join(coincide_vme_poe)}</strong> también minimiza el arrepentimiento (POE), lo que refuerza su solidez.")
    elif best_poe:
        lines.append(f"El POE recomienda <strong>{', '.join(best_poe)}</strong>, distinto al VME, lo que indica que la alternativa más rentable conlleva mayor riesgo de arrepentimiento.")

    if veip is not None and m_vme.get("best_value") is not None:
        pct = veip / abs(m_vme["best_value"]) * 100 if m_vme["best_value"] != 0 else 0
        if pct < 10:
            lines.append(f"El VEIP ({currency}{veip:,.0f}) es bajo en relación al VME, por lo que conseguir información perfecta no cambiaría significativamente la decisión.")
        else:
            lines.append(f"El VEIP ({currency}{veip:,.0f}) representa un {pct:.0f}% del VME óptimo, lo que indica que valdría la pena invertir en mejor información antes de decidir.")

    if not lines:
        return

    content = " ".join(f"<p>{l}</p>" for l in lines)
    st.markdown(f'<div class="insight-box">{content}</div>', unsafe_allow_html=True)


def _render_matrix(results_dict, currency):
    if "decision_df" not in st.session_state or st.session_state.decision_df.empty:
        return

    m_vme = results_dict.get("vme", {})
    m_poe = results_dict.get("poe", {})
    m_max = results_dict.get("maximax", {})
    m_min = results_dict.get("minimax", {})

    df_view = st.session_state.decision_df.copy().set_index("Alternatives")

    if "vme_results" in m_vme:
        vmes = {r["Alternatives"]: r["VME"] for r in m_vme["vme_results"]}
        df_view["VME"] = df_view.index.map(vmes)

    if "poe_results" in m_poe:
        df_view["POE"] = df_view.index.map(m_poe["poe_results"])

    if "resultados" in m_max:
        maxs = {r["Alternatives"]: r["Valor"] for r in m_max["resultados"]}
        df_view["MAX"] = df_view.index.map(maxs)

    if "resultados" in m_min:
        mins = {r["Alternatives"]: r["Valor"] for r in m_min["resultados"]}
        df_view["MIN"] = df_view.index.map(mins)

    best_vme_alts = m_vme.get("best_alternatives", [])
    best_poe_alts = m_poe.get("best_alternatives", [])

    def highlight(df):
        styles = pd.DataFrame("", index=df.index, columns=df.columns)

        if "VME" in df.columns:
            vme_vals = pd.to_numeric(df["VME"], errors="coerce")
            styles.loc[vme_vals == vme_vals.max(), "VME"] = "background-color: #14532d; color: #dcfce7; font-weight: 700;"

        if "POE" in df.columns:
            poe_vals = pd.to_numeric(df["POE"], errors="coerce")
            styles.loc[poe_vals == poe_vals.min(), "POE"] = "background-color: #14532d; color: #dcfce7; font-weight: 700;"
            styles.loc[poe_vals == poe_vals.max(), "POE"] = "background-color: #7f1d1d; color: #fee2e2; font-weight: 700;"

        if "MAX" in df.columns:
            max_vals = pd.to_numeric(df["MAX"], errors="coerce")
            styles.loc[max_vals == max_vals.max(), "MAX"] = "background-color: #1e3a5f; color: #bfdbfe; font-weight: 700;"

        if "MIN" in df.columns:
            min_vals = pd.to_numeric(df["MIN"], errors="coerce")
            styles.loc[min_vals == min_vals.max(), "MIN"] = "background-color: #1e3a5f; color: #bfdbfe; font-weight: 700;"

        return styles

    styled = df_view.style.format(f"{currency}{{:.0f}}").apply(highlight, axis=None)
    st.dataframe(styled, use_container_width=True)

    st.caption("🟢 Verde = mejor valor en ese criterio   🔴 Rojo = peor valor (solo POE)")