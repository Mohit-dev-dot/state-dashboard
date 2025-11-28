import os
st.write("Working directory:", os.getcwd())
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy.stats import linregress
import warnings

from long_summary import generate_long_summary
from impact_summary import generate_impact_summary
from comparison_points import generate_comparison_points
from utils import safe_corr, safe_linreg
from state_profiles import state_profiles

warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="State Development Impact Analyzer (Pro)", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

def apply_custom_theme():
    st.markdown("""<style>
    html, body, .stApp { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    h1, h2, h3, h4 { color: #1a4d94; }
    [data-testid="stMetricDelta"] svg { color: #1a4d94; }
    </style>""", unsafe_allow_html=True)

apply_custom_theme()

@st.cache_data
def load_data(path='data/Project.xlsx'):
    try:
        df = pd.read_excel(path, engine='openpyxl')
        if 'Year' in df.columns:
            df['Year'] = df['Year'].astype(str)
        for c in df.columns:
            if c not in ['State','Year']:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"File not found: {path}. Place Project.xlsx in the data/ folder.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data('data/Project.xlsx')
if df is None:
    st.stop()

available_states = sorted(df['State'].unique())
available_indicators = [c for c in df.columns if c not in ['State','Year']]

default_state = 'Maharashtra' if 'Maharashtra' in available_states else available_states[0]
default_indicator = 'Per Capita Income (₹)' if 'Per Capita Income (₹)' in available_indicators else (available_indicators[0] if available_indicators else None)
default_input = 'Edu Exp (₹ Cr)' if 'Edu Exp (₹ Cr)' in available_indicators else (available_indicators[0] if available_indicators else None)
default_outcome = 'Literacy (%)' if 'Literacy (%)' in available_indicators else (available_indicators[1] if len(available_indicators)>1 else default_input)

try:
    latest_year = df.dropna(subset=[default_indicator])['Year'].max() if default_indicator in df.columns else df['Year'].max()
except Exception:
    latest_year = df['Year'].max()

st.sidebar.title("Dashboard Controls ⚙️")
st.sidebar.caption("Define the parameters for analysis across all tabs.")
st.sidebar.markdown("---")

with st.sidebar.expander("📍 State Focus & Comparison", expanded=True):
    selected_state = st.selectbox('Focus State', options=available_states, index=available_states.index(default_state))
    selected_states_comparison = st.multiselect(
        'Comparison State(s)',
        options=[s for s in available_states if s != selected_state],
        default=[s for s in ['Tamil Nadu', 'Gujarat'] if s in available_states and s != selected_state]
    )
    all_selected_states = sorted(list(set([selected_state] + selected_states_comparison)))

with st.sidebar.expander("📊 Primary Indicator", expanded=True):
    selected_indicator = st.selectbox('Indicator for KPIs/Trend',
                                      options=available_indicators,
                                      index=available_indicators.index(default_indicator) if default_indicator in available_indicators else 0)

with st.sidebar.expander("🔬 Impact Analysis Parameters", expanded=False):
    selected_input = st.selectbox('Input Parameter (X-axis)', options=available_indicators,
                                  index=available_indicators.index(default_input) if default_input in available_indicators else 0)
    outcome_options = [col for col in available_indicators if col != selected_input]
    selected_outcome = st.selectbox('Outcome Parameter (Y-axis)', options=outcome_options,
                                    index=outcome_options.index(default_outcome) if default_outcome in outcome_options else 0)

st.sidebar.markdown("---")
if st.sidebar.checkbox('Show Full Raw Data Table'):
    st.subheader('Raw Data')
    st.dataframe(df)

df_filtered = df[df['State'].isin(all_selected_states)]
df_focus_state = df[df['State'] == selected_state].dropna(subset=[selected_indicator]) if selected_indicator in df.columns else df[df['State'] == selected_state]

st.title('🔬 State Development Impact Analyzer')
st.caption(f"Professional Dashboard | Analysis up to {latest_year}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Dashboard & Summary",
    "📈 Comparative Trend",
    "🔬 Impact Analysis",
    "🏆 Benchmarking & Forecast",
    "📌 State Comparison Insights"
])

with tab1:
    st.header("Long State Summary")
    long_summary_text = generate_long_summary(selected_state, df, selected_indicator, target_lines=50)
    st.markdown(long_summary_text)
    st.markdown("---")
    st.header('Key Performance Indicators (compact)')
    try:
        current_val = df[(df['State'] == selected_state) & (df['Year'] == latest_year)][selected_indicator].dropna().iloc[0]
    except Exception:
        try:
            current_val = df[df['State'] == selected_state][selected_indicator].dropna().iloc[-1]
        except Exception:
            current_val = "N/A"
    col1, col2, col3, col4 = st.columns(4)
    try:
        col1.metric(label=f"Latest Value ({latest_year})", value=f"{current_val:,.2f}" if isinstance(current_val, (int,float,np.number)) else str(current_val))
    except:
        col1.metric(label=f"Latest Value ({latest_year})", value=str(current_val))
    try:
        svals = df[df['State'] == selected_state].dropna(subset=[selected_indicator]).sort_values(by='Year')
        if len(svals) >= 2:
            prev = svals[selected_indicator].iloc[-2]
            yoy = ((svals[selected_indicator].iloc[-1] - prev) / prev) * 100 if prev != 0 else 0
            col2.metric(label="Growth Rate (approx YoY %)", value=f"{yoy:.2f} %", delta_color="normal" if yoy>=0 else "inverse")
        else:
            col2.metric(label="Growth Rate (approx YoY %)", value="N/A")
    except:
        col2.metric(label="Growth Rate (approx YoY %)", value="N/A")
    col3.metric(label="Focus State", value=selected_state)
    col4.metric(label="Indicator", value=selected_indicator)

with tab2:
    st.header(f'Comparative Trend: {selected_indicator}')
    st.caption(f"Comparison for: {', '.join(all_selected_states)}")
    if all_selected_states:
        base = alt.Chart(df_filtered).encode(
            x=alt.X('Year', axis=alt.Axis(title='Year', labelAngle=0)),
            y=alt.Y(selected_indicator, title=selected_indicator),
            color=alt.Color('State', title='State', scale=alt.Scale(scheme='tableau10')),
            tooltip=['State', 'Year', alt.Tooltip(selected_indicator, format=',.2f')]
        ).properties(height=500)
        line = base.mark_line(point=True).encode(size=alt.value(3))
        highlight = alt.selection_point(fields=['State'], on='mouseover', nearest=True)
        chart = (base.mark_circle(size=80).encode(opacity=alt.value(0)).add_params(highlight)
                 + line.encode(opacity=alt.condition(highlight, alt.value(1), alt.value(0.3)))).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Select at least one state for comparison.")

with tab3:
    st.header('Input vs Outcome — Impact Analysis')
    st.caption(f"Assessing the impact of **{selected_input}** on **{selected_outcome}** for **{selected_state}**")
    impact_text = generate_impact_summary(selected_state, df, selected_input, selected_outcome, target_lines=50)
    st.markdown(impact_text)
    try:
        df_latest = df[df['Year'] == latest_year].dropna(subset=[selected_input, selected_outcome])
        if not df_latest.empty and len(df_latest) >= 3:
            scatter = alt.Chart(df_latest).mark_circle(size=120).encode(
                x=alt.X(selected_input, title=selected_input, scale=alt.Scale(zero=False)),
                y=alt.Y(selected_outcome, title=selected_outcome, scale=alt.Scale(zero=False)),
                color=alt.Color('State', legend=None),
                tooltip=['State', alt.Tooltip(selected_input, format=',.0f'), alt.Tooltip(selected_outcome, format='.2f')]
            ).properties(height=420, title=f'{selected_input} vs {selected_outcome} ({latest_year})')
            trend = scatter.transform_regression(selected_input, selected_outcome, method='linear').mark_line(color='#1a4d94', strokeDash=[5,5], size=2)
            st.altair_chart((scatter + trend).interactive(), use_container_width=True)
        else:
            st.info("Not enough cross-state datapoints in the latest year to plot a scatter + trend.")
    except Exception:
        st.info("Scatter plot unavailable due to data format.")

with tab4:
    st.header('Benchmarking & Future Projections')
    col_bench, col_fore = st.columns(2)
    with col_bench:
        st.subheader('State Distribution & Top Performers')
        try:
            df_latest_dist = df[df['Year'] == latest_year].dropna(subset=[selected_indicator])
            if not df_latest_dist.empty:
                bar_chart = alt.Chart(df_latest_dist).mark_bar().encode(
                    x=alt.X(selected_indicator, title=selected_indicator, bin=True),
                    y=alt.Y('count()', title='Count'),
                    color=alt.condition(alt.datum.State == selected_state, alt.value('#1a4d94'), alt.value('#cccccc')),
                ).properties(height=220)
                st.altair_chart(bar_chart, use_container_width=True)
                df_sorted = df_latest_dist.sort_values(by=selected_indicator, ascending=False).reset_index(drop=True)
                top_5 = df_sorted.head(5).rename(columns={selected_indicator: 'Value'})
                st.dataframe(top_5[['State','Value']].style.format({'Value': '{:,.0f}'}).background_gradient(cmap='Blues'), height=220, use_container_width=True)
            else:
                st.warning("No data available for benchmarking on the selected indicator in the latest year.")
        except Exception as e:
            st.error(f"Benchmarking error: {e}")
    with col_fore:
        st.subheader('Future Outlook (Linear Projection)')
        try:
            df_forecast = df[df['State'] == selected_state][['Year', selected_indicator]].copy().dropna()
            df_forecast['Year_Numeric'] = pd.to_numeric(df_forecast['Year'], errors='coerce')
            if len(df_forecast.dropna(subset=['Year_Numeric'])) >= 2:
                latest_year_num = int(df_forecast['Year_Numeric'].max())
                slope, intercept, r_v, p_v, se = linregress(df_forecast['Year_Numeric'], df_forecast[selected_indicator])
                forecast_years_out = st.slider("Select projection years:", 1, 5, 3, key='forecast_slider')
                forecast_years = np.arange(latest_year_num + 1, latest_year_num + forecast_years_out + 1)
                forecast_values = intercept + slope * forecast_years
                forecast_data = pd.DataFrame({'Year': forecast_years.astype(str), selected_indicator: forecast_values})
                df_chart = pd.concat([df_forecast.assign(Type='Historical'), forecast_data.assign(Type='Forecast')], ignore_index=True)
                base = alt.Chart(df_chart).encode(
                    x=alt.X('Year', axis=alt.Axis(title='Year')),
                    y=alt.Y(selected_indicator, title=selected_indicator),
                    tooltip=['Year', alt.Tooltip(selected_indicator, format=',.2f')]
                ).properties(height=250)
                chart = base.mark_line(point=True).encode(
                    color=alt.Color('Type', scale=alt.Scale(range=['#1a4d94', '#e91e63']))
                )
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(forecast_data.set_index('Year'), use_container_width=True)
                st.caption(f"Note: Linear projection (R-squared: {r_v**2:.2f}). Use with caution.")
            else:
                st.warning("Insufficient historical data for forecasting the selected indicator for this state.")
        except Exception as e:
            st.error(f"Forecasting error: {e}")

with tab5:
    st.header("📌 State Comparison Insights — Top 5 Points per Selected State")
    st.caption("Concise, high-value insights that combine the dataset signals with state context.")
    for stname in all_selected_states:
        st.subheader(f"🔹 {stname}")
        pts = generate_comparison_points(stname, df)
        for i, p in enumerate(pts, start=1):
            st.write(f"**{i}. {p}**")
        st.markdown("---")
