import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import linregress
import warnings
import sqlite3
from io import BytesIO

# MAP + SIMULATOR LIBS
import folium
from streamlit_folium import st_folium

# PROJECT MODULES
from long_summary import generate_long_summary
from impact_summary import generate_impact_summary
from comparison_points import generate_comparison_points

warnings.filterwarnings("ignore", category=UserWarning)

# --------------------------------------------------
# PAGE UI CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="State Development Impact Analyzer (Pro)",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_theme():
    st.markdown("""
    <style>
    html, body, .stApp { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    h1, h2, h3, h4 { color: #1a4d94; }
    [data-testid="stMetricDelta"] svg { color: #1a4d94; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# --------------------------------------------------
# LOAD DATA (SQLite)
# --------------------------------------------------

@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect("data/project.db")
        df = pd.read_sql("SELECT * FROM states", conn)
        conn.close()

        if "Year" in df.columns:
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype(int).astype(str)

        for c in df.columns:
            if c not in ["State", "Year"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# --------------------------------------------------
# OPTIONS
# --------------------------------------------------

available_states = sorted(df["State"].unique())
available_indicators = [c for c in df.columns if c not in ["State", "Year"]]

default_state = "Maharashtra" if "Maharashtra" in available_states else available_states[0]
default_indicator = "Per Capita Income (₹)" if "Per Capita Income (₹)" in available_indicators else available_indicators[0]
default_input = "Edu Exp (₹ Cr)" if "Edu Exp (₹ Cr)" in available_indicators else available_indicators[0]

if len(available_indicators) > 1:
    default_outcome = "Literacy (%)" if "Literacy (%)" in available_indicators else available_indicators[1]
else:
    default_outcome = default_input

try:
    latest_year = df.dropna(subset=[default_indicator])["Year"].max()
except Exception:
    latest_year = df["Year"].max()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Controls ⚙️")
st.sidebar.markdown("---")

with st.sidebar.expander("📍 State Focus & Comparison", expanded=True):
    selected_state = st.selectbox(
        "Focus State",
        options=available_states,
        index=available_states.index(default_state)
    )

    selected_states_comparison = st.multiselect(
        "Comparison State(s)",
        options=[s for s in available_states if s != selected_state],
        default=[s for s in ["Tamil Nadu", "Gujarat"] if s in available_states and s != selected_state]
    )

    all_selected_states = sorted(list(set([selected_state] + selected_states_comparison)))

with st.sidebar.expander("📊 Primary Indicator", expanded=True):
    selected_indicator = st.selectbox(
        "Indicator for KPIs/Trend",
        options=available_indicators,
        index=available_indicators.index(default_indicator)
    )

with st.sidebar.expander("🔬 Impact Analysis Parameters", expanded=False):
    selected_input = st.selectbox(
        "Input Parameter (X-axis)",
        options=available_indicators,
        index=available_indicators.index(default_input)
    )

    outcome_options = [col for col in available_indicators if col != selected_input]

    selected_outcome = st.selectbox(
        "Outcome Parameter (Y-axis)",
        options=outcome_options,
        index=outcome_options.index(default_outcome) if default_outcome in outcome_options else 0
    )

st.sidebar.markdown("---")

if st.sidebar.checkbox("Show Full Raw Data Table"):
    st.subheader("Raw Data")
    search = st.text_input("Search State")
    filtered = df[df["State"].str.contains(search, case=False, na=False)] if search else df
    st.dataframe(filtered)

# --------------------------------------------------
# MAIN VIEW
# --------------------------------------------------

df_filtered = df[df["State"].isin(all_selected_states)]

st.title("🔬 State Development Impact Analyzer")
st.caption(f"Professional Dashboard | Analysis up to {latest_year}")

tab1, tab2, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🚀 Dashboard & Summary",
    "📈 Comparative Trend",
    # "🔬 Impact Analysis",
    "🏆 Benchmarking & Forecast",
    "📌 State Comparison Insights",
    "🥇 Leaderboard",
    "🗺️ India Map",
    "🧪 Scenario Simulator"
])

# --------------------------------------------------
# TAB 1 — SUMMARY
# --------------------------------------------------

with tab1:
    st.header("Summary")

    long_summary_text = generate_long_summary(
        selected_state, df, selected_indicator, target_lines=50
    )

    st.markdown(long_summary_text)

    st.markdown("### 📥 Download Summary")
    buffer = BytesIO()
    buffer.write(long_summary_text.encode("utf-8"))
    buffer.seek(0)

    st.download_button(
        label="Download as TXT",
        data=buffer,
        file_name=f"{selected_state}_summary.txt",
        mime="text/plain"
    )

    st.markdown("---")
    st.header("Key Performance Indicators")

    try:
        current_val = df[(df["State"] == selected_state) & (df["Year"] == latest_year)][
            selected_indicator
        ].dropna().iloc[0]
    except:
        current_val = "N/A"

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Latest Value ({latest_year})", current_val)
    c2.metric("Focus State", selected_state)
    c3.metric("Indicator", selected_indicator)

# --------------------------------------------------
# TAB 2 — TREND
# --------------------------------------------------

with tab2:
    st.header(f"Comparative Trend: {selected_indicator}")

    if all_selected_states:
        chart = alt.Chart(df_filtered).mark_line(point=True).encode(
            x="Year",
            y=selected_indicator,
            color="State",
            tooltip=["State", "Year", selected_indicator]
        ).properties(height=450)

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Select at least one state.")

# --------------------------------------------------
# TAB 3 — IMPACT
# --------------------------------------------------

# with tab3:
#     st.header("Input vs Outcome Impact Analysis")

#     text = generate_impact_summary(
#         selected_state, df, selected_input, selected_outcome, target_lines=50
#     )

#     st.markdown(text)

# --------------------------------------------------
# TAB 4 — FORECAST
# --------------------------------------------------

with tab4:
    st.header("Benchmarking & Future Projection")

    try:
        df_forecast = df[df["State"] == selected_state][["Year", selected_indicator]].dropna()
        df_forecast["Year_Numeric"] = pd.to_numeric(df_forecast["Year"], errors="coerce")

        if len(df_forecast) >= 2:
            slope, intercept, *_ = linregress(
                df_forecast["Year_Numeric"], df_forecast[selected_indicator]
            )

            future_years = np.arange(
                df_forecast["Year_Numeric"].max() + 1,
                df_forecast["Year_Numeric"].max() + 4
            )

            forecast = pd.DataFrame({
                "Year": future_years.astype(str),
                selected_indicator: intercept + slope * future_years
            })

            combined = pd.concat([
                df_forecast[["Year", selected_indicator]].assign(Type="Historical"),
                forecast.assign(Type="Forecast")
            ])

            chart = alt.Chart(combined).mark_line(point=True).encode(
                x="Year",
                y=selected_indicator,
                color="Type"
            )

            st.altair_chart(chart, use_container_width=True)
            st.dataframe(forecast)
        else:
            st.info("Not enough data to forecast.")
    except Exception as e:
        st.error(str(e))

# --------------------------------------------------
# TAB 5 — INSIGHTS
# --------------------------------------------------

with tab5:
    st.header("📌 State Comparison Insights")

    for stname in all_selected_states:
        st.subheader(stname)
        pts = generate_comparison_points(stname, df)

        for i, p in enumerate(pts, start=1):
            st.write(f"**{i}. {p}**")

        st.markdown("---")

# --------------------------------------------------
# TAB 6 — LEADERBOARD
# --------------------------------------------------

with tab6:
    st.header("Top & Bottom 5 States")

    metric = st.selectbox("Choose Indicator", available_indicators)

    latest = df[df["Year"] == latest_year][["State", metric]].dropna()

    top = latest.sort_values(metric, ascending=False).head(5)
    bottom = latest.sort_values(metric).head(5)

    st.subheader("Top 5")
    st.dataframe(top)

    st.subheader("Bottom 5")
    st.dataframe(bottom)

# --------------------------------------------------
# TAB 7 — MAP
# --------------------------------------------------

with tab7:
    st.header("India Choropleth Map (Accurate Boundaries)")

    indicator = st.selectbox("Select Indicator for Map", available_indicators)

    try:
        geojson_path = "data/india_states.geojson"

        india = folium.Map(location=[22.5, 79], zoom_start=5)

        latest_df = df[df["Year"] == latest_year][["State", indicator]]

        folium.Choropleth(
            geo_data=geojson_path,
            name="choropleth",
            data=latest_df,
            columns=["State", indicator],
            key_on="feature.properties.NAME_1",
            fill_color="YlGnBu",
            fill_opacity=0.8,
            line_opacity=0.3,
            legend_name=indicator,
        ).add_to(india)

        folium.LayerControl().add_to(india)

        st_folium(india, width=950, height=600)

    except Exception as e:
        st.error(f"Map error: {e}")

# --------------------------------------------------
# TAB 8 — SCENARIO SIMULATOR
# --------------------------------------------------

with tab8:
    st.header("What-If Scenario Simulator")

    inp = st.selectbox("Input Indicator", available_indicators)
    out = st.selectbox("Outcome Indicator", available_indicators)

    change = st.slider("Increase Input (%)", 0, 50, 10)

    df_state = df[df["State"] == selected_state]

    slope = df_state[out].corr(df_state[inp])

    predicted = df_state[out].iloc[-1] + (df_state[out].iloc[-1] * slope * (change / 100))

    st.write(
        f"If **{inp} increases by {change}%**, "
        f"expected **{out} ≈ {predicted:.2f}**"
    )
