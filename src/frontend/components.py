import streamlit as st

def metric_card(label, value, prefix="", suffix="", help_text=""):
    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    ">
        <div style="color: #666; font-size: 14px; margin-bottom: 5px;">{label}</div>
        <div style="color: #333; font-size: 24px; font-weight: bold;">{prefix}{value}{suffix}</div>
        <div style="color: #888; font-size: 12px;">{help_text}</div>
    </div>
    """, unsafe_allow_html=True)

def custom_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #1f77b4;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
        }
        .stMetric {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            padding: 15px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
