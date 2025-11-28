import pandas as pd
from state_profiles import state_profiles


def generate_comparison_points(state, df_full):
    """
    Generates 5 crisp comparison insights for the given state.
    Uses both dataset signals and state profile metadata.
    """

    prof = state_profiles.get(state, {})
    df_state = df_full[df_full['State'] == state].copy()

    points = []

    # -------------------------------------------------------------------
    # 1. If no data for this state → return placeholders
    # -------------------------------------------------------------------
    if df_state.empty:
        return ["No data found for this state."] * 5

    # -------------------------------------------------------------------
    # 2. Identify strongest long-term growth indicator
    # -------------------------------------------------------------------
    growths = {}
    for col in df_state.columns:
        if col not in ['State', 'Year']:
            sub = df_state[['Year', col]].dropna()
            if len(sub) > 1:
                try:
                    a = float(sub[col].iloc[0])
                    b = float(sub[col].iloc[-1])
                    if a != 0:
                        growths[col] = ((b - a) / a) * 100
                except:
                    pass

    if growths:
        top = max(growths, key=growths.get)
        points.append(f"Strongest long-term improvement: **{top}** (+{growths[top]:.1f}%).")
    else:
        points.append("Growth pattern unclear — insufficient long-term data.")

    # -------------------------------------------------------------------
    # 3. Find strongest PCI driver using correlation
    # -------------------------------------------------------------------
    if "Per Capita Income (₹)" in df_state.columns:
        df_num = df_state.drop(columns=['State']).apply(lambda x: pd.to_numeric(x, errors='coerce'))
        corr = df_num.corr()
        if "Per Capita Income (₹)" in corr.columns:
            pci_corr = corr["Per Capita Income (₹)"].drop(labels=["Per Capita Income (₹)"], errors='ignore')
            if not pci_corr.empty:
                driver = pci_corr.abs().idxmax()
                points.append(f"Primary per-capita income driver: **{driver}**.")
            else:
                points.append("Per-capita income driver unclear (weak correlations).")
        else:
            points.append("Not enough data to compute PCI correlation.")
    else:
        points.append("Per-capita income data unavailable.")

    # -------------------------------------------------------------------
    # 4. Identity summary (from real-world profile)
    # -------------------------------------------------------------------
    identity_text = prof.get("summary", ["Profile not available"])[0]
    points.append(f"Identity signal: {identity_text}")

    # -------------------------------------------------------------------
    # 5. Poverty progress
    # -------------------------------------------------------------------
    if "Poverty (%)" in df_state.columns:
        pv = df_state["Poverty (%)"].dropna()
        if len(pv) >= 2:
            points.append(f"Poverty: {pv.iloc[0]:.1f}% → {pv.iloc[-1]:.1f}%.")
        else:
            points.append("Poverty trend incomplete (insufficient data).")
    else:
        points.append("Poverty data unavailable.")

    # -------------------------------------------------------------------
    # 6. Urbanization (latest)
    # -------------------------------------------------------------------
    if "Urbanization (%)" in df_state.columns:
        u = df_state["Urbanization (%)"].dropna()
        if not u.empty:
            points.append(f"Urbanization (latest): {u.iloc[-1]}%.")
        else:
            points.append("Urbanization data missing.")
    else:
        points.append("Urbanization indicator unavailable.")

    return points[:5]
