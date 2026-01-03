"""
MDSA Dashboard - Main Application

Multi-page Streamlit dashboard for MDSA chatbot monitoring.

Pages:
- Welcome: Introduction and setup verification
- Monitor: Real-time monitoring of models, requests, performance
"""

import streamlit as st
import sys
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="MDSA Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .success-banner {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🤖 MDSA Dashboard")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Welcome", "📊 Monitor", "⚙️ Settings"],
    key="navigation"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("""
**MDSA Framework v1.0.0**

Multi-Domain Small Language Model Agentic Orchestration Framework

Features:
- Multi-domain routing
- RAG with ChromaDB
- Tool calling
- Real-time monitoring
- LRU model caching
""")

# Route to selected page
if page == "🏠 Welcome":
    exec(open("pages/welcome.py", encoding="utf-8").read())
elif page == "📊 Monitor":
    exec(open("pages/monitor.py", encoding="utf-8").read())
elif page == "⚙️ Settings":
    exec(open("pages/settings.py", encoding="utf-8").read())
