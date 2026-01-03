"""
Streamlit Monitoring Dashboard for MDSA Chatbot

Real-time monitoring of:
- Model performance
- Request statistics
- Latency metrics
- Domain distribution
- Model loading status
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mdsa import ModelManager, RequestLogger, MetricsCollector


# Page configuration
st.set_page_config(
    page_title="MDSA Chatbot Monitor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stAlert {
        background-color: #d4edda;
        border-color: #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logger' not in st.session_state:
    st.session_state.logger = RequestLogger(max_logs=10000)
if 'metrics' not in st.session_state:
    st.session_state.metrics = MetricsCollector(window_size=1000)
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = ModelManager(max_models=3)

logger = st.session_state.logger
metrics = st.session_state.metrics
model_manager = st.session_state.model_manager

# Title
st.title("🤖 MDSA Chatbot Monitoring Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard Controls")

    refresh = st.button("🔄 Refresh Data", use_container_width=True)

    st.markdown("---")
    st.header("⚙️ Settings")

    auto_refresh = st.checkbox("Auto Refresh (5s)", value=False)
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()

    show_debug = st.checkbox("Show Debug Info", value=False)

    st.markdown("---")
    st.header("ℹ️ About")
    st.info("""
    **MDSA Chatbot Monitor**

    Real-time monitoring for:
    - Request statistics
    - Model performance
    - Latency metrics
    - Domain distribution
    """)

# Get stats
logger_stats = logger.get_stats()
metrics_summary = metrics.get_summary()
model_stats = model_manager.get_stats()

# Overview Metrics
st.header("📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Requests",
        logger_stats['total_requests'],
        delta=None
    )

with col2:
    success_rate = logger_stats['success_rate_percent']
    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%",
        delta=f"{success_rate - 100:.1f}%" if logger_stats['total_requests'] > 0 else None
    )

with col3:
    avg_latency = metrics_summary.get('avg_latency_ms', 0)
    st.metric(
        "Avg Latency",
        f"{avg_latency:.1f}ms",
        delta=None
    )

with col4:
    models_loaded = model_stats['models_loaded']
    max_models = model_stats['max_models']
    st.metric(
        "Models Loaded",
        f"{models_loaded}/{max_models}",
        delta=None
    )

st.markdown("---")

# Two-column layout
col_left, col_right = st.columns([1, 1])

with col_left:
    # Latency Distribution
    st.subheader("⏱️ Latency Distribution")

    if logger_stats['total_requests'] > 0:
        recent_logs = logger.get_recent_logs(count=100)
        latencies = [log.latency_ms for log in recent_logs if log.latency_ms > 0]

        if latencies:
            fig = go.Figure(data=[go.Histogram(
                x=latencies,
                nbinsx=20,
                marker_color='rgb(55, 126, 184)'
            )])

            fig.update_layout(
                xaxis_title="Latency (ms)",
                yaxis_title="Count",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Percentiles
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                st.metric("P50", f"{metrics_summary.get('p50_latency_ms', 0):.1f}ms")
            with p_col2:
                st.metric("P95", f"{metrics_summary.get('p95_latency_ms', 0):.1f}ms")
            with p_col3:
                st.metric("P99", f"{metrics_summary.get('p99_latency_ms', 0):.1f}ms")
        else:
            st.info("No latency data available yet")
    else:
        st.info("No requests processed yet")

    st.markdown("---")

    # Domain Distribution
    st.subheader("🎯 Domain Distribution")

    if logger_stats['total_requests'] > 0:
        recent_logs = logger.get_recent_logs(count=100)
        domains = [log.domain for log in recent_logs]

        if domains:
            domain_counts = pd.Series(domains).value_counts()

            fig = px.pie(
                values=domain_counts.values,
                names=domain_counts.index,
                title="Requests by Domain"
            )

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No domain data available")
    else:
        st.info("No requests processed yet")

with col_right:
    # Model Performance
    st.subheader("🧠 Model Performance")

    if model_stats['models_loaded'] > 0:
        # Show loaded models
        st.write("**Loaded Models:**")
        loaded_models = model_stats.get('loaded_models', [])

        if loaded_models:
            for model in loaded_models:
                st.text(f"✓ {model}")
        else:
            st.info("No models currently loaded")

        # Model memory usage
        total_memory = model_stats.get('total_memory_gb', 0)
        st.metric("Total Model Memory", f"{total_memory:.2f} GB")

    else:
        st.info("No models loaded yet")

    st.markdown("---")

    # Success vs Error Rate
    st.subheader("✅ Success vs Errors")

    if logger_stats['total_requests'] > 0:
        success_count = logger_stats['success_count']
        error_count = logger_stats['error_count']

        fig = go.Figure(data=[
            go.Bar(
                name='Success',
                x=['Requests'],
                y=[success_count],
                marker_color='green'
            ),
            go.Bar(
                name='Errors',
                x=['Requests'],
                y=[error_count],
                marker_color='red'
            )
        ])

        fig.update_layout(
            barmode='stack',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No request data available")

    st.markdown("---")

    # Throughput
    st.subheader("🚀 Throughput")

    throughput = metrics.get_throughput(window_seconds=60)
    st.metric(
        "Requests/Second (60s window)",
        f"{throughput:.2f}",
        delta=None
    )

st.markdown("---")

# Recent Requests Table
st.subheader("📝 Recent Requests")

if logger_stats['total_requests'] > 0:
    recent_logs = logger.get_recent_logs(count=10)

    # Create dataframe
    data = []
    for log in recent_logs:
        data.append({
            'Time': datetime.fromtimestamp(log.timestamp).strftime('%H:%M:%S'),
            'Domain': log.domain,
            'Query': log.query[:50] + '...' if len(log.query) > 50 else log.query,
            'Status': '✅' if log.status == 'success' else '❌',
            'Latency': f"{log.latency_ms:.1f}ms",
            'Confidence': f"{log.confidence:.2f}"
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("No requests logged yet")

# Debug Info
if show_debug:
    st.markdown("---")
    st.subheader("🔧 Debug Information")

    debug_col1, debug_col2 = st.columns(2)

    with debug_col1:
        st.json({
            "Logger Stats": logger_stats,
            "Model Stats": model_stats
        })

    with debug_col2:
        st.json({
            "Metrics Summary": metrics_summary
        })

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | MDSA Framework v1.0.0")
