import pandas as pd
from state_profiles import state_profiles

import math

def generate_long_summary(state, df_full, main_indicator, target_lines=50):
    try:
        profile = state_profiles.get(state, {})
        df_state = df_full[df_full['State'] == state].copy()
        lines = []

        if df_state.empty:
            lines.append(f"# {state} —Summary")
            lines.append("No data available for this state in the uploaded dataset.")
            return "\n".join(lines)

        years = sorted(df_state['Year'].unique())
        min_year, max_year = years[0], years[-1]

        if main_indicator not in df_state.columns:
            lines.append(f"# {state} — Long Summary")
            lines.append(f"Indicator '{main_indicator}' not available for this state.")
            return "\n".join(lines)

        def first_last(col):
            try:
                a = df_state[df_state['Year'] == min_year][col].dropna().iloc[0]
                b = df_state[df_state['Year'] == max_year][col].dropna().iloc[0]
                return float(a), float(b)
            except Exception:
                return None, None

        a, b = first_last(main_indicator)
        change_pct = None
        if a is not None and a != 0:
            change_pct = ((b - a) / a) * 100

        df_num = df_state.drop(columns=['State']).apply(lambda x: pd.to_numeric(x, errors='coerce')) if not df_state.empty else None
        corr = df_num.corr() if df_num is not None else None

        top_pos = {}
        if corr is not None and main_indicator in corr.columns:
            s = corr[main_indicator].drop(labels=[main_indicator], errors='ignore').drop(labels=['Year'], errors='ignore')
            if not s.empty:
                top_pos = s.sort_values(ascending=False).head(3).to_dict()

        growths = {}
        for col in df_state.columns:
            if col not in ['State', 'Year', main_indicator]:
                sub = df_state[['Year', col]].dropna()
                if len(sub) > 1:
                    try:
                        a0 = sub[col].iloc[0]; b0 = sub[col].iloc[-1]
                        if a0 != 0:
                            growths[col] = ((b0 - a0) / a0) * 100
                    except Exception:
                        pass
        top_growth = sorted(growths.items(), key=lambda x: -abs(x[1]))[:4]

        vol = (df_num.std() / df_num.mean()).dropna() if df_num is not None else None
        vol_item = vol.idxmax() if vol is not None and not vol.empty else None

        lines.append(f"# {state} — Development Summary ({min_year} → {max_year})")
        lines.append("")
        lines.append("## 1) Executive overview")
        lines.append(f"- Core profile: {profile.get('notes', 'Profile not available.')}")
        if change_pct is not None:
            trend = "increased" if change_pct > 0 else "decreased"
            lines.append(f"- Headline: **{main_indicator}** has {trend} by **{abs(change_pct):.1f}%** between {min_year} and {max_year}.")
        else:
            lines.append("- Headline: insufficient data to compute start→end change for this indicator.")
        lines.append("")
        lines.append("## 2) Compact numeric snapshot")
        try:
            if 'Per Capita Income (₹)' in df_state.columns:
                pci = df_state['Per Capita Income (₹)'].dropna().iloc[-1]
                lines.append(f"- Per Capita Income (latest): ₹{pci:,.0f}")
        except Exception:
            pass
        try:
            if 'GSDP (₹ Cr)' in df_state.columns:
                g = df_state['GSDP (₹ Cr)'].dropna().iloc[-1]
                lines.append(f"- GSDP (latest): ₹{g:,.0f} Cr")
        except Exception:
            pass
        for k in ['Poverty (%)','Literacy (%)','Urbanization (%)','HDI','SDG Index']:
            try:
                if k in df_state.columns:
                    v = df_state[k].dropna().iloc[-1]
                    lines.append(f"- {k} (latest): {v}")
            except Exception:
                pass
        lines.append("")
        lines.append("## 3) Sectoral strengths (profile + data signals)")
        for s in profile.get('summary', [])[:3]:
            lines.append(f"- {s}")
        if top_growth:
            for col,g in top_growth:
                lines.append(f"- Dataset signal: marked change in **{col}** (~{g:.1f}%).")
        lines.append("")
        lines.append("## 4) Social & human development cues")
        try:
            if 'Literacy (%)' in df_state.columns:
                ls = df_state['Literacy (%)'].dropna()
                if len(ls) > 1:
                    lines.append(f"- Literacy improved from {ls.iloc[0]:.1f}% to {ls.iloc[-1]:.1f}% (start→latest).")
                else:
                    lines.append(f"- Literacy (latest): {ls.iloc[-1] if not ls.empty else 'N/A'}")
        except Exception:
            pass
        try:
            if 'Health Exp (₹ Cr)' in df_state.columns:
                he = df_state['Health Exp (₹ Cr)'].dropna().iloc[-1]
                lines.append(f"- Health budget (latest): ₹{he:,.0f} Cr")
        except Exception:
            pass
        try:
            if 'Edu Exp (₹ Cr)' in df_state.columns:
                ee = df_state['Edu Exp (₹ Cr)'].dropna().iloc[-1]
                lines.append(f"- Education budget (latest): ₹{ee:,.0f} Cr")
        except Exception:
            pass
        lines.append("")
        lines.append("## 5) Infrastructure & urbanization")
        try:
            if 'Urbanization (%)' in df_state.columns:
                u0 = df_state['Urbanization (%)'].dropna().iloc[-1]
                lines.append(f"- Urbanization (latest): {u0}% - shaping services & housing demand.")
        except Exception:
            pass
        try:
            if 'Electrification (%)' in df_state.columns:
                el = df_state['Electrification (%)'].dropna().iloc[-1]
                lines.append(f"- Electrification (latest): {el}%")
        except Exception:
            pass
        if vol_item:
            lines.append(f"- Most volatile indicator in period: **{vol_item}**.")
        lines.append("")
        lines.append("## 6) Poverty, labour & inclusion")
        try:
            if 'Poverty (%)' in df_state.columns:
                p0 = df_state['Poverty (%)'].dropna().iloc[0]
                p1 = df_state['Poverty (%)'].dropna().iloc[-1]
                lines.append(f"- Poverty changed from {p0:.1f}% to {p1:.1f}% (start→latest).")
        except Exception:
            pass
        try:
            if 'Unemployment (%)' in df_state.columns:
                un = df_state['Unemployment (%)'].dropna().iloc[-1]
                lines.append(f"- Unemployment (latest): {un}% (note measurement caveats).")
        except Exception:
            pass
        lines.append("")
        lines.append("## 7) Governance & resilience cues")
        if 'SDG Index' in df_state.columns:
            try:
                s = df_state['SDG Index'].dropna().iloc[-1]
                lines.append(f"- SDG Index (latest): {s} - a multi-dimensional progress marker.")
            except Exception:
                pass
        if state == "Odisha":
            lines.append("- Cyclone and disaster resilience are key policy priorities for sustained growth.")
        if state == "Kerala":
            lines.append("- Demographic ageing and remittance dependence shape fiscal choices.")
        lines.append("")
        lines.append("## 8) Focused recommendations")
        lines.append("- Prioritize investments that improve absorptive capacity (skills, teacher training, health workers).")
        lines.append("- Use targeted capital investments to reduce regional imbalances (transport, irrigation, industrial clusters).")
        lines.append("- Track outcomes (learning, health metrics) not just input budget lines.")
        lines.append("")
        lines.append("## 9) Cross-state pointers")
        lines.append("- Benchmark Per Capita Income elasticity vs peers; identify over-performing states with similar inputs.")
        lines.append("- Use residual analysis to find implementation best-practices to replicate.")
        lines.append("")
        lines.append("## 10) Final synthesis")
        synth = (f"{state} combines structural strengths and policy choices. Use a mix of targeted investments, "
                 "capacity-building and data-driven M&E to convert inputs into sustainable outcomes.")
        lines.append(synth)
        lines.append("")
        current = len(lines)
        extras = [
            "Priority should be on improving service delivery quality.",
            "Pilot, evaluate, scale — keep fidelity to proven models.",
            "Address intra-state disparities with targeted grants and performance monitoring.",
            "Invest in data systems to make outcomes visible at district level.",
            "Align fiscal priorities with measurable social returns."
        ]
        idx = 0
        while current < target_lines:
            suffix = ""
            if idx % 3 == 0 and change_pct is not None:
                suffix = f" (note: main indicator change ≈ {change_pct:.1f}%)."
            lines.append(f"- {extras[idx % len(extras)]}{suffix}")
            idx += 1
            current += 1
        if len(lines) > target_lines:
            lines = lines[:target_lines]
        return "\n".join(lines)
    except Exception as e:
        return f"### Error generating long summary: {e}"
