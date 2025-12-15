
import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_html_tables(url: str, timeout: int = 15):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    try:
        tables = pd.read_html(resp.text)
        return tables
    except Exception:
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        dfs = []
        for t in tables:
            try:
                dfs.append(pd.read_html(str(t))[0])
            except Exception:
                continue
        return dfs

def fetch_table_by_selector(url: str, selector: str, timeout: int = 15):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    el = soup.select_one(selector)
    if el is None:
        return None
    try:
        return pd.read_html(str(el))[0]
    except Exception:
        return None

def fetch_json_api(url: str, params: dict = None, timeout: int = 15):
    resp = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def normalize_state_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    col_map = {c.lower(): c for c in df.columns}
    if 'state' in col_map:
        df = df.rename(columns={col_map['state']: 'State'})
    if 'year' in col_map:
        df = df.rename(columns={col_map['year']: 'Year'})
    for c in df.select_dtypes(include=['object']).columns:
        df[c] = df[c].astype(str).str.strip()
    for c in df.columns:
        if c in ['State', 'Year']:
            continue
        series = df[c].astype(str).str.replace(',', '').str.replace('%', '').replace('nan', '')
        df[c] = pd.to_numeric(series, errors='ignore')
    return df

st.set_page_config(page_title="Auto Data Extract + Insights", layout="wide", page_icon="⚙️")
st.title("Automated Data Extraction + Insights")
st.markdown("Fetch tables from websites/APIs and combine with your Excel dataset for analysis.")

st.sidebar.header("Data sources")
use_local = st.sidebar.checkbox("Use local Project.xlsx (default)", value=True)
uploaded_file = st.sidebar.file_uploader("Or upload Excel file to merge", type=["xlsx", "xls"])

st.sidebar.markdown("---")
st.sidebar.subheader("Web Source (optional)")
url = st.sidebar.text_input("Website / API URL (leave blank if not fetching from web)")
css_selector = st.sidebar.text_input("CSS selector (optional)")

@st.cache_data(ttl=600)
def load_local_excel(fileobj):
    try:
        if fileobj is None:
            return pd.read_excel('Project.xlsx')
        return pd.read_excel(fileobj)
    except Exception as e:
        st.error(f"Failed to load Excel: {e}")
        return None

local_df = load_local_excel(uploaded_file) if use_local else None
web_df = None

if url:
    st.sidebar.markdown("Press Fetch to scrape the URL.")
    if st.sidebar.button("Fetch Data From URL"):
        with st.spinner("Fetching..."):
            try:
                if css_selector:
                    df_sel = fetch_table_by_selector(url, css_selector)
                    tables = [df_sel] if df_sel is not None else fetch_html_tables(url)
                else:
                    tables = fetch_html_tables(url)
                if not tables:
                    st.error("No tables found.")
                else:
                    if len(tables) > 1:
                        idx = st.selectbox("Multiple tables found — choose one", range(len(tables)))
                        web_df = tables[idx]
                    else:
                        web_df = tables[0]
                    st.dataframe(web_df.head(20))
            except Exception as e:
                st.error(f"Error fetching URL: {e}")

if web_df is not None and local_df is not None:
    st.markdown("### Merge options")
    merge_on = st.text_input("Merge on column", "State")
    how = st.selectbox("Merge type", ["left", "inner", "outer", "right"])
    if st.button("Merge web + local"):
        try:
            combined = pd.merge(local_df, normalize_state_table(web_df), on=merge_on, how=how)
            st.session_state['combined_df'] = combined
            st.dataframe(combined.head(20))
        except Exception as e:
            st.error(f"Merge failed: {e}")

elif local_df is not None:
    st.session_state.setdefault('combined_df', local_df)

if web_df is not None and local_df is None:
    st.session_state.setdefault('combined_df', normalize_state_table(web_df))

df = st.session_state.get('combined_df', None)
if df is not None:
    st.markdown("## Data Preview")
    st.write(df.shape)
    if st.checkbox("Show DataFrame"):
        st.dataframe(df)

    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    indicator = st.sidebar.selectbox("Select indicator", numeric_cols) if numeric_cols else None

    if 'State' in df.columns:
        states = sorted(df['State'].dropna().unique())
        selected_states = st.sidebar.multiselect("Filter states", states, default=states[:3])
        df_f = df[df['State'].isin(selected_states)] if selected_states else df
    else:
        df_f = df

    if indicator and 'State' in df.columns and 'Year' in df.columns:
        st.markdown("### YOY & CAGR")
        g = df_f.sort_values(['State', 'Year']).copy()
        g['YOY_%'] = g.groupby('State')[indicator].pct_change() * 100
        st.dataframe(g[['State', 'Year', indicator, 'YOY_%']].head(20))

        def calc_cagr(sub):
            sub = sub.dropna(subset=[indicator, 'Year'])
            if len(sub) < 2:
                return np.nan
            sub = sub.sort_values('Year')
            start, end = sub.iloc[0][indicator], sub.iloc[-1][indicator]
            years = sub.iloc[-1]['Year'] - sub.iloc[0]['Year']
            if years <= 0 or start == 0:
                return np.nan
            return ((end / start) ** (1 / years) - 1) * 100

        cagr = g.groupby('State').apply(calc_cagr).reset_index(name='CAGR_%')
        st.dataframe(cagr.sort_values('CAGR_%', ascending=False).head(10))

    if indicator and 'Year' in df.columns and 'State' in df.columns:
        st.markdown("### Top / Bottom latest year")
        latest = int(df['Year'].dropna().max())
        d = df[df['Year'] == latest]
        topn = st.slider("Top N", 3, 20, 5)
        st.write("Top states", d.nlargest(topn, indicator)[['State', indicator]])
        st.write("Bottom states", d.nsmallest(topn, indicator)[['State', indicator]])

    if len(numeric_cols) >= 2:
        st.markdown("### Correlation Heatmap")
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, ax=ax)
        st.pyplot(fig)

    if indicator and 'State' in df.columns:
        st.markdown("### Anomaly Detection")
        dfa = df[['State', 'Year', indicator]].dropna().copy()
        dfa['z'] = dfa.groupby('State')[indicator].transform(lambda x: (x - x.mean()) / x.std(ddof=0))
        thr = st.slider("Z threshold", 2.0, 4.0, 3.0)
        st.dataframe(dfa[dfa['z'].abs() >= thr])

    if indicator and 'Year' in df.columns and 'State' in df.columns:
        st.markdown("### Simple Forecast")
        if st.button("Run forecast"):
            out = []
            for s, sub in df.dropna(subset=[indicator, 'Year']).groupby('State'):
                sub = sub.sort_values('Year')
                if len(sub) < 2:
                    continue
                x = sub['Year'].values
                y = sub[indicator].values
                b, a = np.polyfit(x, y, 1)
                nxt = x[-1] + 1
                pred = a + b * nxt
                out.append({'State': s, 'Next_Year': nxt, f'Forecast_{indicator}': pred})
            fdf = pd.DataFrame(out)
            st.session_state['forecast'] = fdf
            st.dataframe(fdf)

    st.markdown("### Download")
    if st.button("Download Combined CSV"):
        buf = BytesIO()
        df.to_csv(buf, index=False)
        st.download_button("Save combined.csv", buf.getvalue(), "combined.csv", mime="text/csv")
