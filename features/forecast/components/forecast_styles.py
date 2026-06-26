import streamlit as st

def load_forecast_styles():
    st.markdown("""
    <style>
    .forecast-result-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        border: 1px solid #2a2d3a;
        margin-bottom: 15px;
    }
    .forecast-result-card h4 {
        color: #7b808e;
        font-size: 10px;
        margin-bottom: 8px;
        margin-top: 0;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 600;
    }
    .forecast-result-card h2 {
        color: #4f80ff;
        font-size: 22px;
        margin: 0;
        font-weight: bold;
    }
    .forecast-result-card h3 {
        color: #e5e7eb;
        font-size: 13px;
        margin-top: 6px;
    }
    .forecast-result-card.winner {
        border-color: #4ade80;
        background-color: #142a1e;
    }
    .forecast-result-card.winner h2 {
        color: #4ade80;
    }
    .section-title {
        color: #e5e7eb;
        font-size: 18px;
        font-weight: bold;
        margin: 28px 0 12px;
        border-left: 5px solid #4f80ff;
        padding-left: 12px;
    }
    </style>
    """, unsafe_allow_html=True)