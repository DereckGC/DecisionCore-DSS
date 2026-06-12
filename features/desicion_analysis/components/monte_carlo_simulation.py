import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from features.desicion_analysis.logic.vme import calculate_vme
from features.desicion_analysis.logic.maximax import calculate_maximax
from features.desicion_analysis.logic.minimax import calculate_minimax
from features.desicion_analysis.logic.hurwicz import calculate_hurwicz
from features.desicion_analysis.logic.laplace import calculate_laplace
from features.desicion_analysis.logic.poe import calculate_poe

def run_montecarlo(decision_df, base_probs, alpha, n_simulations, noise=0.05):
    df = decision_df.set_index("Alternatives")
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    alternatives = df.index.tolist()
    payoffs = df.values
    n_alts = len(alternatives)
    n_markets = len(base_probs)

    wins = np.zeros(n_alts, dtype=int)
    all_vmes = [[] for _ in range(n_alts)]
    convergence = []

    conv_step = max(1, n_simulations // 100)

    for i in range(n_simulations):
        perturbed = np.array(base_probs) + np.random.uniform(-noise, noise, n_markets)
        perturbed = np.clip(perturbed, 0.01, None)
        perturbed /= perturbed.sum()

        vmes = payoffs @ perturbed
        winner = np.argmax(vmes)
        wins[winner] += 1

        for j in range(n_alts):
            all_vmes[j].append(vmes[j])

        if (i + 1) % conv_step == 0:
            convergence.append({
                "sim": i + 1,
                **{alternatives[j]: round(wins[j] / (i + 1) * 100, 2) for j in range(n_alts)}
            })

    return {
        "alternatives": alternatives,
        "wins": wins,
        "win_pct": wins / n_simulations * 100,
        "all_vmes": all_vmes,
        "convergence": pd.DataFrame(convergence),
        "n_simulations": n_simulations,
    }

def render_montecarlo():
    st.subheader("Simulación de Montecarlo")

    if "decision_df" not in st.session_state or st.session_state.decision_df.empty:
        st.warning("Primero ingresa datos en la tabla de decisión.")
        return

    probs = st.session_state.get("prob_markets", [])
    markets = [c for c in st.session_state.decision_df.columns if c != "Alternatives"]

    if len(probs) != len(markets):
        st.warning("Las probabilidades no coinciden con los mercados. Verifica la tabla.")
        return

    if abs(sum(probs) - 1.0) > 0.01:
        st.warning("Las probabilidades deben sumar 1.00 antes de simular.")
        return

    currency = st.session_state.get("currency_type", "$")
    alpha = st.session_state.get("alpha_hurwicz", 0.5)

    col1, col2, col3 = st.columns(3)
    n_simulations = col1.select_slider(
        "Número de simulaciones",
        options=[500, 1000, 2000, 5000, 10000, 20000],
        value=5000
    )
    noise = col2.select_slider(
        "Ruido en probabilidades",
        options=[0.01, 0.02, 0.05, 0.08, 0.10, 0.15],
        value=0.05,
        help="Cuánto pueden variar las probabilidades en cada simulación"
    )
    col3.metric("Alpha Hurwicz", alpha)

    if st.button("Ejecutar simulación", type="primary"):
        with st.spinner("Simulando..."):
            result = run_montecarlo(
                st.session_state.decision_df,
                probs,
                alpha,
                n_simulations,
                noise
            )
        st.session_state.montecarlo_result = result

    if "montecarlo_result" not in st.session_state:
        return

    result = st.session_state.montecarlo_result
    alternatives = result["alternatives"]
    wins = result["wins"]
    win_pct = result["win_pct"]
    all_vmes = result["all_vmes"]
    convergence_df = result["convergence"]
    n = result["n_simulations"]

    _render_summary_cards(alternatives, wins, win_pct, n, currency, alpha)
    st.divider()
    _render_win_frequency_chart(alternatives, win_pct)
    st.divider()
    _render_vme_distribution(alternatives, all_vmes, currency)
    st.divider()
    _render_convergence(alternatives, convergence_df)
    st.divider()
    _render_risk_table(alternatives, all_vmes, currency)


def _render_summary_cards(alternatives, wins, win_pct, n, currency, alpha):
    best_idx = int(np.argmax(wins))
    st.markdown("**Resultados de la simulación**")

    cols = st.columns(len(alternatives) + 1)

    with cols[0]:
        st.metric("Simulaciones", f"{n:,}")

    for i, alt in enumerate(alternatives):
        with cols[i + 1]:
            st.metric(
                label=alt,
                value=f"{win_pct[i]:.1f}%",
                delta="ganador" if i == best_idx else None
            )

def _render_win_frequency_chart(alternatives, win_pct):
    st.markdown("**Frecuencia de victoria (% de simulaciones)**")

    colors = px.colors.qualitative.Set2[:len(alternatives)]
    fig = go.Figure(go.Bar(
        x=alternatives,
        y=[round(p, 2) for p in win_pct],
        marker_color=colors,
        text=[f"{p:.1f}%" for p in win_pct],
        textposition="outside"
    ))
    fig.update_layout(
        yaxis_title="% victorias",
        yaxis=dict(range=[0, max(win_pct) * 1.2]),
        height=350,
        margin=dict(t=20, b=20),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_vme_distribution(alternatives, all_vmes, currency):
    st.markdown("**Distribución de VME simulados por alternativa**")

    colors = px.colors.qualitative.Set2[:len(alternatives)]
    fig = go.Figure()

    for i, alt in enumerate(alternatives):
        fig.add_trace(go.Histogram(
            x=all_vmes[i],
            name=alt,
            opacity=0.7,
            marker_color=colors[i],
            nbinsx=40
        ))

    fig.update_layout(
        barmode="overlay",
        xaxis_title=f"VME ({currency})",
        yaxis_title="Frecuencia",
        height=350,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_convergence(alternatives, convergence_df):
    st.markdown("**Convergencia del % de victorias**")

    colors = px.colors.qualitative.Set2[:len(alternatives)]
    fig = go.Figure()

    for i, alt in enumerate(alternatives):
        if alt in convergence_df.columns:
            fig.add_trace(go.Scatter(
                x=convergence_df["sim"],
                y=convergence_df[alt],
                name=alt,
                mode="lines",
                line=dict(color=colors[i], width=1.5)
            ))

    fig.update_layout(
        xaxis_title="Número de simulaciones",
        yaxis_title="% victorias",
        height=300,
        margin=dict(t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_risk_table(alternatives, all_vmes, currency):
    st.markdown("**Tabla de estadísticas de riesgo**")

    rows = []
    for i, alt in enumerate(alternatives):
        arr = np.array(all_vmes[i])
        rows.append({
            "Alternativa": alt,
            "VME promedio": round(np.mean(arr)),
            "Desv. estándar": round(np.std(arr)),
            "Mínimo": round(np.min(arr)),
            "Percentil 10%": round(np.percentile(arr, 10)),
            "Mediana": round(np.median(arr)),
            "Percentil 90%": round(np.percentile(arr, 90)),
            "Máximo": round(np.max(arr)),
        })

    risk_df = pd.DataFrame(rows).set_index("Alternativa")
    fmt = {col: lambda v: f"{currency}{v:,.0f}" for col in risk_df.columns}
    st.dataframe(risk_df.style.format(fmt), use_container_width=True)