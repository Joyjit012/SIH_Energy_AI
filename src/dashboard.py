import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Smart Energy Management",
    page_icon="⚡",
    layout="wide"
)


# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/energy_management_results.csv"
    )

    df["utc_timestamp"] = pd.to_datetime(
        df["utc_timestamp"]
    )

    return df


df = load_data()


# ==========================================
# TITLE
# ==========================================

st.title("⚡ Smart AI-Driven Energy Management System")

st.write(
    "AI-based renewable energy prediction and "
    "smart energy optimization for polar research stations."
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Dashboard Controls")

max_rows = st.sidebar.slider(
    "Number of hours to display",
    min_value=24,
    max_value=min(1000, len(df)),
    value=min(168, len(df))
)

display_df = df.head(max_rows)


# ==========================================
# KEY METRICS
# ==========================================

latest = df.iloc[-1]


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Renewable Energy",
        f"{latest['total_renewable']:.2f} kWh"
    )


with col2:

    st.metric(
        "Load Demand",
        f"{latest['load_prediction']:.2f} kWh"
    )


with col3:

    st.metric(
        "Battery SOC",
        f"{latest['battery_soc']:.1f}%"
    )


with col4:

    st.metric(
        "Generator",
        f"{latest['generator']:.2f} kWh"
    )


# ==========================================
# CURRENT ACTION
# ==========================================

st.subheader("🔄 Current Energy Management Action")

st.info(
    str(latest["action"])
)


# ==========================================
# RENEWABLE GENERATION
# ==========================================

st.subheader("☀️ Solar and 🌬️ Wind Prediction")

fig1 = px.line(
    display_df,
    x="utc_timestamp",
    y=[
        "solar_prediction",
        "wind_prediction"
    ],
    labels={
        "value": "Energy (kWh)",
        "utc_timestamp": "Time"
    }
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# LOAD VS RENEWABLE
# ==========================================

st.subheader("⚡ Renewable Energy vs Load")

fig2 = px.line(
    display_df,
    x="utc_timestamp",
    y=[
        "total_renewable",
        "load_prediction"
    ],
    labels={
        "value": "Energy (kWh)",
        "utc_timestamp": "Time"
    }
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==========================================
# BATTERY SOC
# ==========================================

st.subheader("🔋 Battery State of Charge")

fig3 = px.line(
    display_df,
    x="utc_timestamp",
    y="battery_soc",
    labels={
        "battery_soc": "SOC (%)",
        "utc_timestamp": "Time"
    }
)

fig3.update_yaxes(
    range=[0, 100]
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==========================================
# GENERATOR
# ==========================================

st.subheader("⛽ Generator Usage")

fig4 = px.area(
    display_df,
    x="utc_timestamp",
    y="generator",
    labels={
        "generator": "Generator (kWh)",
        "utc_timestamp": "Time"
    }
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ==========================================
# FLEXIBLE LOAD
# ==========================================

st.subheader("🔄 Flexible Load Reduction")

fig5 = px.bar(
    display_df,
    x="utc_timestamp",
    y="flexible_reduction",
    labels={
        "flexible_reduction":
            "Reduction (kWh)",

        "utc_timestamp":
            "Time"
    }
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# ==========================================
# ENERGY SUMMARY
# ==========================================

st.subheader("📊 Overall Energy Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)


with summary_col1:

    st.metric(
        "Total Renewable",
        f"{df['total_renewable'].sum():,.2f} kWh"
    )


with summary_col2:

    st.metric(
        "Total Generator",
        f"{df['generator'].sum():,.2f} kWh"
    )


with summary_col3:

    st.metric(
        "Total Flexible Reduction",
        f"{df['flexible_reduction'].sum():,.2f} kWh"
    )


# ==========================================
# RECENT DATA
# ==========================================

st.subheader("📋 Energy Management Data")

st.dataframe(
    display_df.tail(20),
    use_container_width=True
)