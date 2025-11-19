# # # from .state_profiles import state_profiles
# # # from .utils import safe_corr, safe_linreg
# # # import math

# # # def generate_impact_summary(state, df_full, input_indicator, outcome_indicator, target_lines=50):
# # #     try:
# # #         profile = state_profiles.get(state, {})
# # #         df_state = df_full[df_full['State'] == state].copy()
# # #         lines = []

# # #         if df_state.empty:
# # #             lines.append(f"# Impact Analysis — {state}")
# # #             lines.append("No state-level data available.")
# # #             return "\n".join(lines)
# # #         if input_indicator not in df_state.columns or outcome_indicator not in df_state.columns:
# # #             lines.append(f"# Impact Analysis — {state}: {input_indicator} -> {outcome_indicator}")
# # #             lines.append("Selected indicators not available both in dataset for this state.")
# # #             return "\n".join(lines)

# # #         years = sorted(df_state['Year'].unique())
# # #         min_year, max_year = years[0], years[-1]
# # #         latest_year = max_year

# # #         df_latest_all = df_full[df_full['Year'] == latest_year].dropna(subset=[input_indicator, outcome_indicator])
# # #         cross_r = safe_corr(df_latest_all[input_indicator], df_latest_all[outcome_indicator]) if not df_latest_all.empty else float('nan')

# # #         df_ts = df_state[['Year', input_indicator, outcome_indicator]].dropna()
# # #         ts_r = safe_corr(df_ts[input_indicator], df_ts[outcome_indicator]) if not df_ts.empty else float('nan')

# # #         reg_outcome = safe_linreg(df_ts['Year'].astype(float), df_ts[outcome_indicator]) if not df_ts.empty else None
# # #         if reg_outcome:
# # #             slope_out, intercept_out, r_out, p_out, se_out = reg_outcome
# # #         else:
# # #             slope_out = intercept_out = r_out = p_out = se_out = float('nan')

# # #         cross_reg = safe_linreg(df_latest_all[input_indicator], df_latest_all[outcome_indicator]) if not df_latest_all.empty else None
# # #         cross_slope = cross_intercept = cross_rval = float('nan')
# # #         if cross_reg:
# # #             cross_slope, cross_intercept, cross_rval, _, _ = cross_reg

# # #         residual_note = "Residual not computed (data insufficient)."
# # #         try:
# # #             state_latest = df_state[df_state['Year'] == latest_year].dropna(subset=[input_indicator, outcome_indicator])
# # #             if cross_reg and not state_latest.empty:
# # #                 x_val = float(state_latest[input_indicator].iloc[-1])
# # #                 y_val = float(state_latest[outcome_indicator].iloc[-1])
# # #                 y_hat = cross_intercept + cross_slope * x_val
# # #                 residual = y_val - y_hat
# # #                 residual_note = f"Latest-year residual (actual - predicted) = {residual:.2f} (positive means over-performing relative to peers given input)."
# # #         except Exception:
# # #             pass

# # #         lines.append(f"# Impact Analysis — {state}: {input_indicator} -> {outcome_indicator}")
# # #         lines.append("")
# # #         lines.append("## 1) Key quantitative diagnostics")
# # #         lines.append(f"- Analysis window (state time-series): {min_year} -> {max_year}")
# # #         if not math.isnan(cross_r):
# # #             lines.append(f"- Cross-state (latest year {latest_year}) correlation r = {cross_r:.3f}")
# # #         else:
# # #             lines.append("- Cross-state correlation not available or insufficient.")
# # #         if not math.isnan(ts_r):
# # #             lines.append(f"- State time-series correlation r = {ts_r:.3f}")
# # #         else:
# # #             lines.append("- State time-series correlation not available or insufficient.")
# # #         if not math.isnan(slope_out):
# # #             lines.append(f"- Trend in outcome (time-series slope) ≈ {slope_out:.4f} per year; R² ≈ {r_out**2:.3f}")
# # #         else:
# # #             lines.append("- Trend regression on outcome not feasible due to data constraints.")
# # #         lines.append(f"- Efficiency note: {residual_note}")
# # #         lines.append("")
# # #         lines.append("## 2) Interpreting relationships")
# # #         if not math.isnan(cross_r):
# # #             if cross_r >= 0.7:
# # #                 lines.append("- Cross-state: strong positive relationship; scaling input across states is associated with higher outcomes.")
# # #             elif cross_r >= 0.3:
# # #                 lines.append("- Cross-state: moderate positive relationship.")
# # #             elif cross_r >= -0.3:
# # #                 lines.append("- Cross-state: weak or inconclusive relationship.")
# # #             else:
# # #                 lines.append("- Cross-state: negative relationship — suggests potential misallocation or measurement issues.")
# # #         else:
# # #             lines.append("- Cross-state evidence insufficient to determine general relationship.")
# # #         if not math.isnan(ts_r):
# # #             if ts_r >= 0.7:
# # #                 lines.append("- Within this state: strong positive time-series relationship — increases in input historically accompany increases in outcome.")
# # #             elif ts_r >= 0.3:
# # #                 lines.append("- Within this state: moderate positive association.")
# # #             elif ts_r >= -0.3:
# # #                 lines.append("- Within this state: weak or no clear temporal association.")
# # #             else:
# # #                 lines.append("- Within this state: negative association — may indicate inefficiency or reverse causality.")
# # #         else:
# # #             lines.append("- No reliable within-state time-series association found.")
# # #         lines.append("")
# # #         lines.append("## 3) Causal pathways & mechanisms (state-specific)")
# # #         prof_notes = profile.get('notes','')
# # #         if 'service' in prof_notes.lower() or 'finance' in prof_notes.lower() or 'it' in prof_notes.lower():
# # #             lines.append("- In service-led economies, inputs like education show returns by enabling higher-skilled employment and productivity.")
# # #         if state == "Kerala":
# # #             lines.append("- Kerala: high base capacity often means small inputs can produce noticeable outcome improvements; but diminishing returns can appear at high levels.")
# # #         if state == "Odisha":
# # #             lines.append("- Odisha: converting inputs to outcomes may require upfront infrastructure or institutional investments due to spatial disparities.")
# # #         if state == "Gujarat":
# # #             lines.append("- Gujarat: strong private absorption suggests that public inputs that catalyze private linkages may have high leverage.")
# # #         lines.append("- Always check supply-side constraints (staff availability, infrastructure) which modulate impact.")
# # #         lines.append("")
# # #         lines.append("## 4) Implementation diagnostics")
# # #         lines.append("- Check whether funds are distributed equitably across districts; concentration in a few districts reduces statewide impact.")
# # #         lines.append("- Assess service quality: e.g., for education, measure learning outcomes, not just enrolment or expenditure.")
# # #         lines.append("- For health: focus on coverage, staff availability, and supply chains rather than nominal budgets alone.")
# # #         lines.append("")
# # #         lines.append("## 5) Recommendations")
# # #         lines.append("- Strengthen M&E: track inputs -> outputs -> outcomes with district-level dashboards.")
# # #         lines.append("- Pilot targeted interventions in lagging districts and scale what works with fidelity.")
# # #         lines.append("- Improve absorptive capacity: training, procurement efficiency, and local governance strength.")
# # #         lines.append("- Use cross-state positive outliers (residual-positive states) as learning labs for process reforms.")
# # #         lines.append("")
# # #         lines.append("## 6) State vignettes")
# # #         if state == "Maharashtra":
# # #             lines.append("- Maharashtra: link education inputs to Mumbai-Pune service clusters to improve job absorption.")
# # #         if state == "Tamil Nadu":
# # #             lines.append("- Tamil Nadu: strong manufacturing ecosystem suggests vocational/technical investments may translate rapidly to outcomes.")
# # #         if state == "Kerala":
# # #             lines.append("- Kerala: small, well-targeted investments in health and education often yield visible human development gains.")
# # #         lines.append("")
# # #         lines.append("## 7) Quantitative appendix (paraphrased)")
# # #         lines.append(f"- Cross-state slope (if computable) ≈ {cross_slope:.4f} (units outcome per unit input) ; cross-r ≈ {cross_r:.3f}")
# # #         if not math.isnan(slope_out):
# # #             lines.append(f"- State outcome trend slope ≈ {slope_out:.4f} ; time-series r ≈ {ts_r:.3f}")
# # #         lines.append("")
# # #         current = len(lines)
# # #         seeds = [
# # #             "Focus on equity in allocation to ensure outcomes are inclusive.",
# # #             "Use pilot -> evaluate -> scale for adaptive program design.",
# # #             "Complement financial inputs with capacity-building and governance reforms.",
# # #             "Track service quality indicators to detect implementation gaps early.",
# # #             "Leverage private sector partnerships selectively where public delivery is weak."
# # #         ]
# # #         idx = 0
# # #         while current < target_lines:
# # #             suffix = ""
# # #             if idx % 2 == 0 and not math.isnan(ts_r):
# # #                 suffix = f" (ts_r={ts_r:.3f})"
# # #             lines.append(f"- {seeds[idx % len(seeds)]}{suffix}")
# # #             idx += 1
# # #             current += 1
# # #         if len(lines) > target_lines:
# # #             lines = lines[:target_lines]
# # #         return "\n".join(lines)
# # #     except Exception as e:
# # #         return f"### Error generating impact summary: {e}"



# # # modules/impact_summary.py
# # import pandas as pd
# # import numpy as np
# # from .state_profiles import state_profiles
# # from .utils import safe_corr, safe_linreg

# # def _first_last_change(df_state, col):
# #     """Return (first, last, pct_change). Values can be None."""
# #     try:
# #         series = df_state[col].dropna()
# #         if series.empty:
# #             return None, None, None
# #         a = float(series.iloc[0])
# #         b = float(series.iloc[-1])
# #         pct = ((b - a) / a) * 100 if a != 0 else None
# #         return a, b, pct
# #     except Exception:
# #         return None, None, None

# # def _latest_value(df_state, col):
# #     try:
# #         v = df_state[col].dropna().iloc[-1]
# #         return float(v)
# #     except Exception:
# #         return None

# # def _fmt(val, suffix=''):
# #     if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
# #         return "N/A"
# #     if isinstance(val, float) and float(val).is_integer():
# #         val = int(val)
# #     try:
# #         return f"{val:,}{suffix}"
# #     except Exception:
# #         return str(val) + suffix

# # def generate_impact_summary(state, df_full, input_indicator, outcome_indicator, target_lines=50):
# #     """
# #     Ground-level Impact Analysis (policy-facing).
# #     Covers 12 areas:
# #     1) Employment & incomes
# #     2) Poverty reduction
# #     3) Agriculture outcomes
# #     4) Industrial & service sector growth
# #     5) Urbanization & migration
# #     6) Health outcomes
# #     7) Education & skill development
# #     8) Infrastructure improvements
# #     9) Social welfare outcomes
# #     10) Inequality & regional disparities
# #     11) Governance & ease of living
# #     12) Environment & sustainability

# #     Returns a multi-line string ~ target_lines lines.
# #     """

# #     try:
# #         prof = state_profiles.get(state, {})
# #         df_state = df_full[df_full['State'] == state].copy()
# #         lines = []

# #         if df_state.empty:
# #             lines.append(f"# Ground Impact Report — {state}")
# #             lines.append("No state-level data available in dataset.")
# #             return "\n".join(lines)

# #         years = sorted(df_state['Year'].unique())
# #         min_year, max_year = years[0], years[-1]
# #         latest_year = max_year

# #         header = f"# Ground Impact Report — {state} ({min_year} → {max_year})"
# #         lines.append(header)
# #         lines.append("")  # spacer

# #         # Title context
# #         lines.append("## Executive summary (tl;dr)")
# #         # compute main indicator change if possible
# #         a_main, b_main, main_pct = _first_last_change(df_state, input_indicator) if input_indicator in df_state.columns else (None, None, None)
# #         a_out, b_out, out_pct = _first_last_change(df_state, outcome_indicator) if outcome_indicator in df_state.columns else (None, None, None)

# #         # short executive synthesis
# #         exec_parts = []
# #         if main_pct is not None:
# #             exec_parts.append(f"{input_indicator} changed by {main_pct:.1f}% (start→latest).")
# #         if out_pct is not None:
# #             exec_parts.append(f"{outcome_indicator} changed by {out_pct:.1f}%.")
# #         if prof.get('summary'):
# #             exec_parts.append(prof['summary'][0])
# #         if not exec_parts:
# #             lines.append("- Quick note: insufficient numeric signals; qualitative profile used instead.")
# #         else:
# #             lines.append("- " + " ".join(exec_parts))
# #         lines.append("")

# #         # Precompute many useful pairs
# #         vals = {}
# #         cols_of_interest = {
# #             'pci': 'Per Capita Income (₹)',
# #             'gsdp': 'GSDP (₹ Cr)',
# #             'poverty': 'Poverty (%)',
# #             'literacy': 'Literacy (%)',
# #             'urban': 'Urbanization (%)',
# #             'edu_exp': 'Edu Exp (₹ Cr)',
# #             'health_exp': 'Health Exp (₹ Cr)',
# #             'agri_exp': 'Agri Exp (₹ Cr)',
# #             'ind_exp': 'Ind Exp (₹ Cr)',
# #             'serv_exp': 'Serv Exp (₹ Cr)',
# #             'elect': 'Electrification (%)',
# #             'san': 'Sanitation (%)',
# #             'pipe': 'Piped Water (%)',
# #             'hdi': 'HDI',
# #             'sdg': 'SDG Index',
# #             'imr': 'IMR',
# #             'life': 'Life Expectancy',
# #             'skill': 'Skill Coverage (%)',
# #             'housing': 'Urban Housing Units (Lakh)',
# #             'unemp': 'Unemployment (%)'
# #         }
# #         for k, col in cols_of_interest.items():
# #             if col in df_state.columns:
# #                 vals[k] = {
# #                     'first': _first_last_change(df_state, col)[0],
# #                     'last': _first_last_change(df_state, col)[1],
# #                     'pct': _first_last_change(df_state, col)[2],
# #                     'latest': _latest_value(df_state, col)
# #                 }
# #             else:
# #                 vals[k] = {'first': None, 'last': None, 'pct': None, 'latest': None}

# #         # Helper to explain direction
# #         def trend_text(pct):
# #             if pct is None:
# #                 return "no clear trend"
# #             if pct > 20:
# #                 return "strong increase"
# #             if pct > 5:
# #                 return "moderate increase"
# #             if pct > -5:
# #                 return "stable / marginal change"
# #             if pct > -20:
# #                 return "moderate decline"
# #             return "sharp decline"

# #         # 1. Employment & incomes
# #         lines.append("## 1) Employment & incomes")
# #         emp_notes = []
# #         # use Unemployment, Per Capita Income, GSDP, Service/Industry spend as proxies
# #         un = vals['unemp']['latest']
# #         pci_pct = vals['pci']['pct']
# #         gsdp_pct = vals['gsdp']['pct']
# #         serv_pct = vals['serv_exp']['pct']
# #         ind_pct = vals['ind_exp']['pct']
# #         if un is not None:
# #             emp_notes.append(f"Latest reported unemployment ≈ { _fmt(un, '%') }.")
# #         if pci_pct is not None:
# #             emp_notes.append(f"Per-capita income shows a {trend_text(pci_pct)} ({pci_pct:.1f}%).")
# #         if gsdp_pct is not None:
# #             emp_notes.append(f"GSDP shows {trend_text(gsdp_pct)} ({gsdp_pct:.1f}%).")
# #         # infer employment pattern
# #         if serv_pct and serv_pct > (ind_pct or -999):
# #             emp_notes.append("Service sector growth likely absorbed a substantial share of new jobs — urban employment expanded.")
# #         elif ind_pct and ind_pct > (serv_pct or -999):
# #             emp_notes.append("Industrial expansion likely translated into manufacturing & construction jobs.")
# #         if not emp_notes:
# #             emp_notes.append("Limited direct employment signals in dataset; recommend using PLFS/household surveys for micro-level inference.")
# #         for s in emp_notes:
# #             lines.append(f"- {s}")
# #         lines.append("")

# #         # 2. Poverty reduction
# #         lines.append("## 2) Poverty reduction")
# #         p0 = vals['poverty']['first']; p1 = vals['poverty']['last']; ppct = vals['poverty']['pct']
# #         if p0 is None:
# #             lines.append("- Poverty indicator missing; cannot quantify progress.")
# #         else:
# #             if ppct is not None and ppct < 0:
# #                 lines.append(f"- Poverty reduced from {p0:.1f}% to {p1:.1f}%, a {abs(ppct):.1f}% decline overall; this likely improved consumption among the bottom deciles.")
# #             elif ppct is not None:
# #                 lines.append(f"- Poverty changed from {p0:.1f}% to {p1:.1f}% ({ppct:.1f}%).")
# #             else:
# #                 lines.append(f"- Poverty data present but trend unclear.")
# #         lines.append("")

# #         # 3. Agriculture outcomes
# #         lines.append("## 3) Agriculture outcomes")
# #         agri_pct = vals['agri_exp']['pct']
# #         # agricultural outcomes sometimes seen via agri_exp and GSDP/agri share - use agri_exp
# #         if agri_pct is not None:
# #             if agri_pct > 10:
# #                 lines.append(f"- Agricultural spending grew ~{agri_pct:.1f}%, supporting higher input subsidies, procurement or irrigation projects — likely positive for yields where irrigation exists.")
# #             else:
# #                 lines.append(f"- Agricultural spending change (~{agri_pct:.1f}%) modest; ground-level gains depend on irrigation coverage and market access.")
# #         else:
# #             lines.append("- Agri spending data limited; check district-level crop and procurement records for real outcomes.")
# #         # mention rural distress if poverty high
# #         if p1 is not None and p1 > 20:
# #             lines.append("- Elevated poverty suggests persistent rural distress which may limit effective agricultural investment benefits.")
# #         lines.append("")

# #         # 4. Industrial & service sector growth
# #         lines.append("## 4) Industrial & service sector growth")
# #         if ind_pct is not None:
# #             lines.append(f"- Industry spending trend: {trend_text(ind_pct)} ({ind_pct:.1f}%).")
# #         else:
# #             lines.append("- Industry spending data not available to infer depth of industrialization.")
# #         if serv_pct is not None:
# #             lines.append(f"- Services spending trend: {trend_text(serv_pct)} ({serv_pct:.1f}%).")
# #         # on-ground implications
# #         if (serv_pct and serv_pct > 20) or (ind_pct and ind_pct > 20):
# #             lines.append("- On the ground this tends to mean faster job creation in urban areas, increased demand for housing and transport, and supply-chain spillovers.")
# #         else:
# #             lines.append("- Growth appears moderate; transformative structural employment shifts are likely gradual.")
# #         lines.append("")

# #         # 5. Urbanization & migration
# #         lines.append("## 5) Urbanization & migration")
# #         urb_pct = vals['urban']['pct']; urb_latest = vals['urban']['latest']
# #         if urb_latest is not None:
# #             lines.append(f"- Urbanization (latest): { _fmt(urb_latest, '%') }.")
# #             if urb_pct is not None and urb_pct > 5:
# #                 lines.append("- Rapid urbanization implies higher demand for urban housing, services and transit; slum/upgrading pressures may rise.")
# #             else:
# #                 lines.append("- Urbanization pace moderate; migration patterns are likely sector-driven (services/industry).")
# #         else:
# #             lines.append("- Urbanization metric unavailable.")
# #         # housing pointer
# #         if vals['housing']['latest'] is not None:
# #             lines.append(f"- Urban housing stock (Lakh): {_fmt(vals['housing']['latest'])} — track affordability.")
# #         lines.append("")

# #         # 6. Health outcomes
# #         lines.append("## 6) Health outcomes")
# #         he_pct = vals['health_exp']['pct']; life_latest = vals['life']['latest']; imr_latest = vals['imr']['latest']
# #         if he_pct is not None:
# #             lines.append(f"- Health expenditure trend: {trend_text(he_pct)} ({he_pct:.1f}%).")
# #         if imr_latest is not None:
# #             lines.append(f"- IMR (latest): { _fmt(imr_latest) } per 1000 — direct proxy for neonatal & maternal care effectiveness.")
# #         if life_latest is not None:
# #             lines.append(f"- Life expectancy (latest): { _fmt(life_latest) } years — broad health & nutrition signal.")
# #         if he_pct is None and imr_latest is None and life_latest is None:
# #             lines.append("- Health signals limited; consider facility-level health management indicators.")
# #         lines.append("")

# #         # 7. Education & skill development
# #         lines.append("## 7) Education & skill development")
# #         ed_pct = vals['edu_exp']['pct']; lit_first = vals['literacy']['first']; lit_last = vals['literacy']['last']
# #         skill_latest = vals['skill']['latest']
# #         if ed_pct is not None:
# #             lines.append(f"- Education spending change: {trend_text(ed_pct)} ({ed_pct:.1f}%).")
# #         if lit_last is not None and lit_first is not None:
# #             lines.append(f"- Literacy: {lit_first:.1f}% → {lit_last:.1f}% (start→latest).")
# #         if skill_latest is not None:
# #             lines.append(f"- Skill coverage (latest): { _fmt(skill_latest, '%') } — important for employability.")
# #         if (ed_pct is None and lit_last is None and skill_latest is None):
# #             lines.append("- Education/skill signals limited in dataset; use enrollment/learning outcome surveys for ground truth.")
# #         lines.append("")

# #         # 8. Infrastructure improvements
# #         lines.append("## 8) Infrastructure improvements")
# #         el_latest = vals['elect']['latest']; pipe_latest = vals['pipe']['latest']; san_latest = vals['san']['latest']
# #         infra_notes = []
# #         if el_latest is not None:
# #             infra_notes.append(f"Electrification: {_fmt(el_latest, '%')}")
# #         if pipe_latest is not None:
# #             infra_notes.append(f"Piped water: {_fmt(pipe_latest, '%')}")
# #         if san_latest is not None:
# #             infra_notes.append(f"Sanitation access: {_fmt(san_latest, '%')}")
# #         if infra_notes:
# #             lines.append("- " + "; ".join(infra_notes) + ". These translate directly to quality-of-life improvements if service reliability is ensured.")
# #         else:
# #             lines.append("- Basic infrastructure signals missing.")
# #         lines.append("")

# #         # 9. Social welfare outcomes
# #         lines.append("## 9) Social welfare & human development")
# #         hdi_latest = vals['hdi']['latest']; sdg_latest = vals['sdg']['latest']
# #         if hdi_latest is not None:
# #             lines.append(f"- HDI (latest): {_fmt(hdi_latest)} — composite of health, education and income.")
# #         if sdg_latest is not None:
# #             lines.append(f"- SDG Index (latest): {_fmt(sdg_latest)} — useful for policy prioritization.")
# #         if hdi_latest is None and sdg_latest is None:
# #             lines.append("- Social progress indicators missing; outcomes should be monitored with population-level surveys.")
# #         lines.append("")

# #         # 10. Inequality & regional disparities
# #         lines.append("## 10) Inequality & regional disparities")
# #         # dataset often lacks direct inequality measures; use urbanization & PCI vs poverty as proxies
# #         if vals['pci']['pct'] is not None and vals['poverty']['pct'] is not None:
# #             if vals['pci']['pct'] and vals['poverty']['pct'] and vals['pci']['pct'] > 0 and vals['poverty']['pct'] > -10:
# #                 lines.append("- Rising per-capita income alongside modest poverty decline suggests gains concentrated among middle/upper strata; inequality risks should be examined.")
# #             else:
# #                 lines.append("- Patterns suggest inclusive gains; verify with district-wise distributional data.")
# #         else:
# #             lines.append("- Inequality cannot be reliably inferred from available columns; recommend collecting consumption/asset surveys.")
# #         # regional disparities note from profile
# #         if "dispar" in prof.get('notes', '').lower() or "regional" in prof.get('notes', '').lower():
# #             lines.append(f"- Note from profile: {prof.get('notes')}")
# #         lines.append("")

# #         # 11. Governance & ease of living
# #         lines.append("## 11) Governance & ease of living")
# #         if sdg_latest is not None:
# #             lines.append(f"- SDG Index indicates multi-sector governance performance: {_fmt(sdg_latest)}.")
# #         if vals['elect']['latest'] and vals['san']['latest']:
# #             lines.append("- Improvements in electrification and sanitation signal better public provisioning and service reach.")
# #         else:
# #             lines.append("- Governance signals incomplete; use contract-delivery metrics for deeper insights.")
# #         lines.append("")

# #         # 12. Environment & sustainability
# #         lines.append("## 12) Environment & sustainability")
# #         # we rely on profile hints for env impacts (mining, coastal, water stress)
# #         notes = prof.get('notes', '')
# #         if "mineral" in notes.lower() or "mining" in notes.lower():
# #             lines.append("- Mineral-intensive economy: monitor pollution, land reclamation and community rehabilitation.")
# #         if "coast" in notes.lower() or "coastal" in notes.lower():
# #             lines.append("- Coastal vulnerability and port-driven growth imply attention to resilience and habitat impacts.")
# #         if "agri" in notes.lower() or vals['agri_exp']['pct'] is not None:
# #             lines.append("- Agriculture intensification may stress water resources; prioritize sustainable irrigation.")
# #         if all("min" not in notes.lower() and "coast" not in notes.lower() and vals['agri_exp']['pct'] is None):
# #             lines.append("- Environmental signals not explicit in dataset; pair with satellite / pollution / water data for monitoring.")
# #         lines.append("")

# #         # Final synthesis + recommendations (concise)
# #         lines.append("## Final synthesis & recommended actions (practical)")
# #         synth = [
# #             "1) Use district-level dashboards to track inputs -> outputs -> outcomes (health, learning, poverty).",
# #             "2) Prioritize investments that increase absorptive capacity: teachers, health workers, municipal service staff.",
# #             "3) Target lagging districts with integrated packages (connectivity + skills + market access).",
# #             "4) Monitor equity indicators (consumption/asset surveys) to detect widening inequality early.",
# #             "5) Combine financial inputs with governance reforms (procurement, staffing, M&E)."
# #         ]
# #         for s in synth:
# #             lines.append(f"- {s}")

# #         # pad/truncate to target_lines
# #         if len(lines) < target_lines:
# #             filler = [
# #                 "Track service quality (not just budgets) to measure impact.",
# #                 "Pilot locally, evaluate quickly, then scale with fidelity.",
# #                 "Use public-private partnerships where service delivery is weak.",
# #                 "Improve local feedback loops (citizen reports, grievance redress)."
# #             ]
# #             idx = 0
# #             while len(lines) < target_lines:
# #                 lines.append(f"- {filler[idx % len(filler)]}")
# #                 idx += 1
# #         elif len(lines) > target_lines:
# #             lines = lines[:target_lines]

# #         return "\n".join(lines)

# #     except Exception as e:
# #         return f"### Error generating ground impact summary: {e}"



# # modules/impact_summary.py
# import pandas as pd
# import numpy as np
# from .state_profiles import state_profiles
# from .utils import safe_corr, safe_linreg

# # ------------------------- Helper Functions -----------------------------

# def _first_last_change(df_state, col):
#     """Return (first, last, pct_change) for given column."""
#     try:
#         series = df_state[col].dropna()
#         if series.empty:
#             return None, None, None
#         a = float(series.iloc[0])
#         b = float(series.iloc[-1])
#         pct = ((b - a) / a) * 100 if a != 0 else None
#         return a, b, pct
#     except:
#         return None, None, None


# def _latest_value(df_state, col):
#     try:
#         v = df_state[col].dropna().iloc[-1]
#         return float(v)
#     except:
#         return None


# def _fmt(val, suffix=''):
#     """Pretty format numbers."""
#     if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
#         return "N/A"
#     try:
#         if isinstance(val, float) and val.is_integer():
#             val = int(val)
#         return f"{val:,}{suffix}"
#     except:
#         return str(val) + suffix


# def trend_text(pct):
#     """Convert numeric change into a descriptive trend."""
#     if pct is None:
#         return "no clear trend"
#     if pct > 20:
#         return "strong increase"
#     if pct > 5:
#         return "moderate increase"
#     if pct > -5:
#         return "stable / marginal"
#     if pct > -20:
#         return "moderate decline"
#     return "sharp decline"


# # ----------------------------- Main Function -----------------------------

# def generate_impact_summary(state, df_full, input_indicator, outcome_indicator, target_lines=50):
#     """
#     Generates a 12-dimension ground-level impact analysis (~50 lines):

#     1) Employment & incomes
#     2) Poverty reduction
#     3) Agriculture outcomes
#     4) Industrial & service sector growth
#     5) Urbanization & migration
#     6) Health outcomes
#     7) Education & skill development
#     8) Infrastructure improvements
#     9) Social welfare outcomes
#     10) Inequality & regional disparities
#     11) Governance & ease of living
#     12) Environment & sustainability
#     """
#     try:
#         profile = state_profiles.get(state, {})
#         df_state = df_full[df_full["State"] == state].copy()

#         lines = []

#         # -------------------------------------
#         # Basic validation
#         # -------------------------------------
#         if df_state.empty:
#             return f"# Ground Impact Report — {state}\n\nNo data available."

#         years = sorted(df_state["Year"].unique())
#         min_year, max_year = years[0], years[-1]

#         # -------------------------------------
#         # Header
#         # -------------------------------------
#         lines.append(f"# Ground Impact Report — {state} ({min_year} → {max_year})\n")

#         # -------------------------------------
#         # Executive summary
#         # -------------------------------------
#         lines.append("## Executive Summary")

#         a_in, b_in, pct_in = _first_last_change(df_state, input_indicator) if input_indicator in df_state.columns else (None, None, None)
#         a_out, b_out, pct_out = _first_last_change(df_state, outcome_indicator) if outcome_indicator in df_state.columns else (None, None, None)

#         summary_parts = []
#         if pct_in is not None:
#             summary_parts.append(f"{input_indicator} changed by {pct_in:.1f}%")
#         if pct_out is not None:
#             summary_parts.append(f"{outcome_indicator} changed by {pct_out:.1f}%")
#         if profile.get("summary"):
#             summary_parts.append(profile["summary"][0])

#         if summary_parts:
#             lines.append("- " + ". ".join(summary_parts) + ".")
#         else:
#             lines.append("- Limited numeric signals; relying partly on qualitative profile.")

#         lines.append("")

#         # -------------------------------------
#         # Precompute useful indicators
#         # -------------------------------------
#         indicators = {
#             "pci": "Per Capita Income (₹)",
#             "gsdp": "GSDP (₹ Cr)",
#             "poverty": "Poverty (%)",
#             "literacy": "Literacy (%)",
#             "urban": "Urbanization (%)",
#             "edu": "Edu Exp (₹ Cr)",
#             "health": "Health Exp (₹ Cr)",
#             "agri": "Agri Exp (₹ Cr)",
#             "ind": "Ind Exp (₹ Cr)",
#             "serv": "Serv Exp (₹ Cr)",
#             "elect": "Electrification (%)",
#             "san": "Sanitation (%)",
#             "pipe": "Piped Water (%)",
#             "hdi": "HDI",
#             "sdg": "SDG Index",
#             "imr": "IMR",
#             "life": "Life Expectancy",
#             "skill": "Skill Coverage (%)",
#             "housing": "Urban Housing Units (Lakh)",
#             "unemp": "Unemployment (%)",
#         }

#         vals = {}
#         for key, col in indicators.items():
#             if col in df_state.columns:
#                 first, last, pct = _first_last_change(df_state, col)
#                 latest = _latest_value(df_state, col)
#                 vals[key] = {"first": first, "last": last, "pct": pct, "latest": latest}
#             else:
#                 vals[key] = {"first": None, "last": None, "pct": None, "latest": None}

#         # =========================================================
#         # 1) Employment & incomes
#         # =========================================================
#         lines.append("## 1) Employment & incomes")
#         un = vals["unemp"]["latest"]
#         pci_pct = vals["pci"]["pct"]
#         gsdp_pct = vals["gsdp"]["pct"]
#         ind_pct = vals["ind"]["pct"]
#         serv_pct = vals["serv"]["pct"]

#         if un is not None:
#             lines.append(f"- Unemployment (latest): {_fmt(un, '%')}.")
#         if pci_pct is not None:
#             lines.append(f"- Per-capita income shows a {trend_text(pci_pct)} ({pci_pct:.1f}%).")
#         if gsdp_pct is not None:
#             lines.append(f"- GSDP trend: {trend_text(gsdp_pct)} ({gsdp_pct:.1f}%).")

#         # Sector-based employment inference
#         if serv_pct is not None and ind_pct is not None:
#             if serv_pct > ind_pct:
#                 lines.append("- Service sector growth likely generated IT, retail, logistics and urban jobs.")
#             elif ind_pct > serv_pct:
#                 lines.append("- Industrial expansion likely increased manufacturing & construction jobs.")
#         else:
#             lines.append("- Insufficient data to identify which sector drove employment.")

#         lines.append("")

#         # =========================================================
#         # 2) Poverty reduction
#         # =========================================================
#         lines.append("## 2) Poverty reduction")
#         p0, p1, ppct = vals["poverty"]["first"], vals["poverty"]["last"], vals["poverty"]["pct"]

#         if p0 is not None and p1 is not None:
#             if ppct is not None and ppct < 0:
#                 lines.append(f"- Poverty decreased from {p0:.1f}% → {p1:.1f}%.")
#             else:
#                 lines.append(f"- Poverty changed from {p0:.1f}% → {p1:.1f}%.")
#         else:
#             lines.append("- Poverty data unavailable.")

#         lines.append("")

#         # =========================================================
#         # 3) Agriculture outcomes
#         # =========================================================
#         lines.append("## 3) Agriculture outcomes")
#         agri_pct = vals["agri"]["pct"]

#         if agri_pct is not None:
#             if agri_pct > 10:
#                 lines.append(f"- Agriculture expenditure rose significantly (~{agri_pct:.1f}%), improving irrigation, procurement or subsidy support.")
#             else:
#                 lines.append(f"- Agriculture expenditure changed ~{agri_pct:.1f}%; moderate impact expected.")
#         else:
#             lines.append("- Agriculture expenditure data unavailable.")

#         lines.append("")

#         # =========================================================
#         # 4) Industrial & service sector growth  (FIXED)
#         # =========================================================
#         lines.append("## 4) Industrial & service sector growth")

#         if ind_pct is not None:
#             lines.append(f"- Industry spending trend: {trend_text(ind_pct)} ({ind_pct:.1f}%).")
#         else:
#             lines.append("- Industry data unavailable.")

#         if serv_pct is not None:
#             lines.append(f"- Services spending trend: {trend_text(serv_pct)} ({serv_pct:.1f}%).")
#         else:
#             lines.append("- Services data unavailable.")

#         if ind_pct is not None and serv_pct is not None:
#             if serv_pct > ind_pct:
#                 lines.append("- Services likely contributed more to structural growth and jobs.")
#             elif ind_pct > serv_pct:
#                 lines.append("- Industrial spending indicates stronger manufacturing expansion.")
#         else:
#             lines.append("- Cannot compare industrial vs service growth due to missing values.")

#         lines.append("")

#         # =========================================================
#         # 5) Urbanization & migration
#         # =========================================================
#         lines.append("## 5) Urbanization & migration")
#         urb = vals["urban"]["latest"]; urb_pct = vals["urban"]["pct"]

#         if urb is not None:
#             lines.append(f"- Urbanization (latest): {_fmt(urb, '%')}.")
#             if urb_pct is not None and urb_pct > 5:
#                 lines.append("- Rapid urbanization suggests migration toward cities for jobs.")
#             else:
#                 lines.append("- Urbanization growth moderate; migration more sector-specific.")
#         else:
#             lines.append("- Urbanization data unavailable.")

#         lines.append("")

#         # =========================================================
#         # 6) Health outcomes
#         # =========================================================
#         lines.append("## 6) Health outcomes")
#         he = vals["health"]["pct"]; imr = vals["imr"]["latest"]; life = vals["life"]["latest"]

#         if he is not None:
#             lines.append(f"- Health expenditure: {trend_text(he)} ({he:.1f}%).")
#         if imr is not None:
#             lines.append(f"- IMR (latest): {_fmt(imr)} per 1000.")
#         if life is not None:
#             lines.append(f"- Life expectancy (latest): {_fmt(life)} years.")

#         lines.append("")

#         # =========================================================
#         # 7) Education & skill development
#         # =========================================================
#         lines.append("## 7) Education & skill development")
#         ed_pct = vals["edu"]["pct"]; lit0 = vals["literacy"]["first"]; lit1 = vals["literacy"]["last"]
#         skill = vals["skill"]["latest"]

#         if ed_pct is not None:
#             lines.append(f"- Education expenditure: {trend_text(ed_pct)} ({ed_pct:.1f}%).")
#         if lit0 is not None and lit1 is not None:
#             lines.append(f"- Literacy improved from {lit0:.1f}% → {lit1:.1f}%.")
#         if skill is not None:
#             lines.append(f"- Skill coverage (latest): {_fmt(skill, '%')}.")

#         lines.append("")

#         # =========================================================
#         # 8) Infrastructure improvements
#         # =========================================================
#         lines.append("## 8) Infrastructure improvements")
#         electr = vals["elect"]["latest"]; pipe = vals["pipe"]["latest"]; san = vals["san"]["latest"]

#         infra = []
#         if electr is not None: infra.append(f"Electrification {_fmt(electr, '%')}")
#         if pipe is not None: infra.append(f"Piped water {_fmt(pipe, '%')}")
#         if san is not None: infra.append(f"Sanitation {_fmt(san, '%')}")

#         if infra:
#             lines.append("- " + "; ".join(infra) + ".")
#         else:
#             lines.append("- No infrastructure indicators available.")

#         lines.append("")

#         # =========================================================
#         # 9) Social welfare outcomes
#         # =========================================================
#         lines.append("## 9) Social welfare outcomes")
#         hdi = vals["hdi"]["latest"]; sdg = vals["sdg"]["latest"]

#         if hdi is not None:
#             lines.append(f"- HDI (latest): {_fmt(hdi)}.")
#         if sdg is not None:
#             lines.append(f"- SDG Index (latest): {_fmt(sdg)}.")

#         lines.append("")

#         # =========================================================
#         # 10) Inequality & regional disparities
#         # =========================================================
#         lines.append("## 10) Inequality & regional disparities")

#         if pci_pct is not None and vals["poverty"]["pct"] is not None:
#             if pci_pct > 0 and vals["poverty"]["pct"] > -10:
#                 lines.append("- Income growth appears uneven; poverty hasn't reduced proportionally.")
#             else:
#                 lines.append("- Data suggests more inclusive income gains.")
#         else:
#             lines.append("- Inequality cannot be inferred from available indicators.")

#         lines.append("")

#         # =========================================================
#         # 11) Governance & ease of living
#         # =========================================================
#         lines.append("## 11) Governance & ease of living")
#         if sdg is not None:
#             lines.append(f"- SDG Index reflects multi-sector governance outcome: {_fmt(sdg)}.")
#         if electr and san:
#             lines.append("- Improvements in electrification and sanitation suggest stronger service delivery.")
#         lines.append("")

#         # =========================================================
#         # 12) Environment & sustainability
#         # =========================================================
#         lines.append("## 12) Environment & sustainability")
#         notes = profile.get("notes", "").lower()

#         if "coast" in notes:
#             lines.append("- Coastal vulnerabilities require climate resilience planning.")
#         if "mineral" in notes or "mining" in notes:
#             lines.append("- Mining-linked economy requires monitoring of land & pollution impacts.")
#         if "agri" in notes or vals["agri"]["pct"] is not None:
#             lines.append("- Agricultural stress may affect water sustainability.")

#         lines.append("")

#         # =========================================================
#         # Final synthesis
#         # =========================================================
#         lines.append("## Final Synthesis")
#         lines.append("- Improve district-level monitoring.")
#         lines.append("- Link spending more tightly to measurable outcomes.")
#         lines.append("- Strengthen last-mile service delivery.")
#         lines.append("- Address inequality through targeted welfare.")
#         lines.append("")

#         # pad to target_lines
#         fillers = [
#             "Improve data systems for real-time governance.",
#             "Promote skill development aligned with industry needs.",
#             "Strengthen urban local bodies for better service delivery."
#         ]
#         idx = 0
#         while len(lines) < target_lines:
#             lines.append("- " + fillers[idx % len(fillers)])
#             idx += 1

#         return "\n".join(lines)

#     except Exception as e:
#         return f"### Error generating ground impact summary: {e}"



# modules/impact_summary.py
# import pandas as pd
# import numpy as np
# from .state_profiles import state_profiles

# # ---------- Helpers ----------
# def _first_last(df_state, col):
#     try:
#         s = df_state[col].dropna()
#         if s.empty:
#             return None, None, None
#         a = float(s.iloc[0]); b = float(s.iloc[-1])
#         pct = ((b - a) / a) * 100 if a != 0 else None
#         return a, b, pct
#     except Exception:
#         return None, None, None

# def _latest(df_state, col):
#     try:
#         v = df_state[col].dropna().iloc[-1]
#         return float(v)
#     except Exception:
#         return None

# def _fmt(val, suffix=""):
#     if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
#         return "N/A"
#     try:
#         if isinstance(val, float) and val.is_integer():
#             val = int(val)
#         return f"{val:,}{suffix}"
#     except:
#         return str(val) + suffix

# def _trend_word(pct):
#     if pct is None:
#         return "no clear trend"
#     if pct > 20:
#         return "strong increase"
#     if pct > 5:
#         return "moderate increase"
#     if pct > -5:
#         return "stable / marginal change"
#     if pct > -20:
#         return "moderate decline"
#     return "sharp decline"

# # ---------- Indicator-specific templates ----------
# # Each function returns a list of lines (strings) relevant to that indicator.
# def _impact_literacy(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Literacy (%)")
#     edu_pct = _first_last(df_state, "Edu Exp (₹ Cr)")[2]
#     skill = _latest(df_state, "Skill Coverage (%)")
#     pci_pct = _first_last(df_state, "Per Capita Income (₹)")[2]

#     lines.append(f"**Focus:** Literacy (what changed on the ground).")
#     if pct is not None:
#         lines.append(f"- Literacy { _trend_word(pct) } ({pct:.1f}% from start→latest).")
#     else:
#         lines.append("- Literacy trend not computable from available data.")

#     if edu_pct is not None:
#         lines.append(f"- Education spending shows a { _trend_word(edu_pct) } ({edu_pct:.1f}%), which is a likely supply-side driver.")
#     else:
#         lines.append("- Education spending data limited — check district budgets and teacher recruitment for implementation insights.")

#     if skill is not None:
#         lines.append(f"- Skill coverage (latest): {_fmt(skill, '%')}. This supports transition from schooling to employment.")
#     if pci_pct is not None and pct is not None and pci_pct > 0 and pct > 0:
#         lines.append("- Rising literacy accompanied by income growth suggests improved learning-to-earnings pathways.")
#     lines.append("- Ground-level impacts to check: school completion rates, transition to secondary schooling, learning outcomes (tests), teacher attendance, and mid-day meal coverage.")
#     lines.append("- Equity lens: examine gender and rural/urban gaps in literacy improvements.")
#     # pad/truncate
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: link education inputs to measurable learning outcomes and remedial programs.")
#     return lines[:target_lines]

# def _impact_pci(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Per Capita Income (₹)")
#     poverty_first, poverty_last, poverty_pct = _first_last(df_state, "Poverty (%)")
#     gdp_pct = _first_last(df_state, "GSDP (₹ Cr)")[2]

#     lines.append("**Focus:** Per Capita Income (PC I) — household-level income & consumption.")
#     if pct is not None:
#         lines.append(f"- Per-capita income { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- PCI trend not computable.")

#     if gdp_pct is not None:
#         lines.append(f"- GSDP shows { _trend_word(gdp_pct) } ({gdp_pct:.1f}%), indicating macro demand that can raise incomes.")
#     if poverty_last is not None:
#         lines.append(f"- Poverty (start→latest): { _fmt(poverty_first) } → { _fmt(poverty_last) } (%).")
#         if poverty_pct is not None and poverty_pct < 0 and pct is not None and pct > 0:
#             lines.append("- Income gains appear to have contributed to poverty reduction; verify distributional coverage across districts.")
#     lines.append("- Ground impacts: higher household consumption, stronger informal sector demand, possible rise in savings/credit uptake, and urban consumer demand.")
#     lines.append("- Verify whether gains are inclusive: check wage growth for lowest deciles, female labor participation, and rural vs urban divergence.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: use household consumption surveys and PSU/regional accounts to verify depth of income gains.")
#     return lines[:target_lines]

# def _impact_gsdp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "GSDP (₹ Cr)")
#     ind_pct = _first_last(df_state, "Ind Exp (₹ Cr)")[2]
#     serv_pct = _first_last(df_state, "Serv Exp (₹ Cr)")[2]

#     lines.append("**Focus:** GSDP — the economy's aggregate output.")
#     if pct is not None:
#         lines.append(f"- GSDP shows a { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- GSDP trend not computable.")

#     if ind_pct is not None or serv_pct is not None:
#         lines.append("- Sectoral drivers:")
#         if ind_pct is not None:
#             lines.append(f"  - Industry spending: { _trend_word(ind_pct) } ({ind_pct:.1f}%).")
#         if serv_pct is not None:
#             lines.append(f"  - Services spending: { _trend_word(serv_pct) } ({serv_pct:.1f}%).")
#     lines.append("- On the ground this may translate into job creation (sector-specific), higher tax revenues, and greater fiscal space for public services.")
#     lines.append("- Check whether growth is broad-based (across districts and sectors) or concentrated in a few urban hubs.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: link GSDP growth to employment and poverty indicators for ground validation.")
#     return lines[:target_lines]

# def _impact_poverty(state, df_state, in_indicator, target_lines):
#     lines = []
#     p0,p1,pct = _first_last(df_state, "Poverty (%)")
#     pci_pct = _first_last(df_state, "Per Capita Income (₹)")[2]
#     lines.append("**Focus:** Poverty — bottom-of-pyramid outcomes.")
#     if pct is not None:
#         if pct < 0:
#             lines.append(f"- Poverty declined by {abs(pct):.1f}% from {p0:.1f}% to {p1:.1f}%. This likely improved baseline consumption and health outcomes for low-income households.")
#         else:
#             lines.append(f"- Poverty changed by {pct:.1f}% ({p0:.1f}% → {p1:.1f}%).")
#     else:
#         lines.append("- Poverty trend not computable from data.")
#     if pci_pct is not None:
#         lines.append(f"- Per-capita income trend: {_trend_word(pci_pct)} ({pci_pct:.1f}%) — important for sustained poverty reduction.")
#     lines.append("- Ground checks: social protection coverage, access to subsidized food, livelihoods programs and public works participation rates.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: prioritize targeting in districts with persistent poverty and monitor benefit take-up.")
#     return lines[:target_lines]

# def _impact_urbanization(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Urbanization (%)")
#     housing = _latest(df_state, "Urban Housing Units (Lakh)")
#     lines.append("**Focus:** Urbanization — migration & city growth.")
#     if pct is not None:
#         lines.append(f"- Urbanization { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Urbanization trend not computable.")
#     if housing is not None:
#         lines.append(f"- Urban housing stock (latest): {_fmt(housing)} Lakh — check affordability & services.")
#     lines.append("- On-ground impacts: higher demand for housing, transport, sanitation; possible informal settlement growth.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: plan for urban infrastructure, affordable housing and slum-upgrading.")
#     return lines[:target_lines]

# def _impact_edu_exp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Edu Exp (₹ Cr)")
#     lit = _first_last(df_state, "Literacy (%)")[2]
#     lines.append("**Focus:** Education Expenditure — schooling & learning inputs.")
#     if pct is not None:
#         lines.append(f"- Education spending { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Education spending trend not computable.")
#     if lit is not None:
#         lines.append(f"- Literacy trend: {_trend_word(lit)} ({lit:.1f}%).")
#     lines.append("- Ground-level impact depends on spending composition: teacher hiring, school infrastructure, learning materials, and remedial programs.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: measure learning outcomes (not just inputs) and strengthen teacher training.")
#     return lines[:target_lines]

# def _impact_health_exp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Health Exp (₹ Cr)")
#     imr = _latest(df_state, "IMR")
#     life = _latest(df_state, "Life Expectancy")
#     lines.append("**Focus:** Health Expenditure — coverage & outcomes.")
#     if pct is not None:
#         lines.append(f"- Health spending { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Health spending trend not computable.")
#     if imr is not None:
#         lines.append(f"- IMR (latest): {_fmt(imr)} per 1000 — primary proxy for neonatal & maternal care.")
#     if life is not None:
#         lines.append(f"- Life expectancy (latest): {_fmt(life)} years.")
#     lines.append("- Ground impacts hinge on service readiness: staff, supplies, referral systems and primary care access.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: strengthen PHC systems and monitor essential health service coverage.")
#     return lines[:target_lines]

# def _impact_agri_exp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Agri Exp (₹ Cr)")
#     lines.append("**Focus:** Agriculture Expenditure — farm incomes & productivity.")
#     if pct is not None:
#         lines.append(f"- Agri spending { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Agriculture spending trend not computable.")
#     lines.append("- Ground-level effects: irrigation, input subsidies, extension services and market linkages determine yield & farmer income outcomes.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: accompany spending with market access and crop diversification support.")
#     return lines[:target_lines]

# def _impact_ind_exp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Ind Exp (₹ Cr)")
#     lines.append("**Focus:** Industrial Expenditure — manufacturing & construction.")
#     if pct is not None:
#         lines.append(f"- Industrial spending { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Industrial spending trend not computable.")
#     lines.append("- On the ground: this tends to create factory, construction and supply-chain employment; monitor skills and safety compliance.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: support linkages to MSMEs and local supplier development.")
#     return lines[:target_lines]

# def _impact_serv_exp(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Serv Exp (₹ Cr)")
#     lines.append("**Focus:** Services Expenditure — trade, finance, IT, tourism.")
#     if pct is not None:
#         lines.append(f"- Services spending { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Services spending trend not computable.")
#     lines.append("- Ground effects: urban jobs, higher tertiary education demand, and increased consumer services.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: invest in vocational training aligned to service-demand.")
#     return lines[:target_lines]

# def _impact_electrification(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Electrification (%)")
#     lines.append("**Focus:** Electrification — access to electricity.")
#     if pct is not None:
#         lines.append(f"- Electrification { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Electrification trend not computable.")
#     lines.append("- Ground-level impact: better lighting, refrigeration, small-enterprise productivity, and education-study hours.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: monitor reliability and hours of supply, not just connections.")
#     return lines[:target_lines]

# def _impact_sanitation(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Sanitation (%)")
#     lines.append("**Focus:** Sanitation — public health and dignity.")
#     if pct is not None:
#         lines.append(f"- Sanitation access { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Sanitation trend not computable.")
#     lines.append("- Ground impacts: reductions in water-borne diseases, improved school attendance for girls, and household time savings.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: link hardware investments to behaviour-change campaigns.")
#     return lines[:target_lines]

# def _impact_piped_water(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Piped Water (%)")
#     lines.append("**Focus:** Piped Water — water access & reliability.")
#     if pct is not None:
#         lines.append(f"- Piped water access { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Piped water trend not computable.")
#     lines.append("- Ground effects: reduced collection time, better hygiene, and improved health outcomes if quality is ensured.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: monitor service quality and coverage gaps.")
#     return lines[:target_lines]

# def _impact_hdi(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "HDI")
#     lines.append("**Focus:** HDI — composite human development.")
#     if pct is not None:
#         lines.append(f"- HDI { _trend_word(pct) } ({pct:.2f}%).")
#     else:
#         lines.append("- HDI trend not computable.")
#     lines.append("- HDI improvements indicate combined gains in health, education and income; drill down to subcomponents for targeted actions.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: use HDI submetrics to prioritize interventions.")
#     return lines[:target_lines]

# def _impact_sdg(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "SDG Index")
#     lines.append("**Focus:** SDG Index — multi-sector policy outcomes.")
#     if pct is not None:
#         lines.append(f"- SDG Index { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- SDG Index trend not computable.")
#     lines.append("- Use SDG sub-indicators to identify sectoral bottlenecks and prioritize cross-cutting reforms.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: align budget priorities to SDG gaps identified.")
#     return lines[:target_lines]

# def _impact_imr(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "IMR")
#     lines.append("**Focus:** Infant Mortality Rate (IMR) — neonatal & maternal health signal.")
#     if pct is not None:
#         lines.append(f"- IMR changed by {pct:.1f}% ({_fmt(a)} → {_fmt(b)}).")
#     else:
#         lines.append("- IMR trend not computable.")
#     lines.append("- Ground-level impacts: measure facility births, neonatal care coverage, and nutrition programs.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: strengthen primary maternal & neonatal systems.")
#     return lines[:target_lines]

# def _impact_life_expectancy(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Life Expectancy")
#     lines.append("**Focus:** Life Expectancy — long-term health & welfare signal.")
#     if pct is not None:
#         lines.append(f"- Life expectancy { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Life expectancy trend not computable.")
#     lines.append("- Improvements reflect cumulative gains in nutrition, healthcare, water and sanitation.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: track disease-specific mortality and health service access.")
#     return lines[:target_lines]

# def _impact_skill(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Skill Coverage (%)")
#     lines.append("**Focus:** Skill Coverage — employability & vocational readiness.")
#     if pct is not None:
#         lines.append(f"- Skill coverage { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Skill coverage trend not computable.")
#     lines.append("- Ground impact: higher skill coverage should reduce structural unemployment and improve wage outcomes if matched to industry demand.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: measure placement rates and employer satisfaction.")
#     return lines[:target_lines]

# def _impact_housing(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Urban Housing Units (Lakh)")
#     lines.append("**Focus:** Urban Housing — stock & affordability.")
#     if pct is not None:
#         lines.append(f"- Urban housing stock { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Urban housing trend not computable.")
#     lines.append("- Ground effects: affordability pressures, peri-urban growth, and infrastructure needs.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: monitor price-to-income and rental affordability metrics.")
#     return lines[:target_lines]

# def _impact_unemployment(state, df_state, in_indicator, target_lines):
#     lines = []
#     a,b,pct = _first_last(df_state, "Unemployment (%)")
#     lines.append("**Focus:** Unemployment — labour market slack.")
#     if pct is not None:
#         lines.append(f"- Unemployment { _trend_word(pct) } ({pct:.1f}%).")
#     else:
#         lines.append("- Unemployment trend not computable.")
#     lines.append("- Ground-level impacts: youth joblessness, underemployment in rural areas, and migration pressures.")
#     while len(lines) < target_lines:
#         lines.append("- Recommendation: combine short-term public works with skill programs for quick absorption.")
#     return lines[:target_lines]

# # ---------- Dispatcher mapping ----------
# DISPATCH = {
#     "Literacy (%)": _impact_literacy,
#     "Per Capita Income (₹)": _impact_pci,
#     "GSDP (₹ Cr)": _impact_gsdp,
#     "Poverty (%)": _impact_poverty,
#     "Urbanization (%)": _impact_urbanization,
#     "Edu Exp (₹ Cr)": _impact_edu_exp,
#     "Health Exp (₹ Cr)": _impact_health_exp,
#     "Agri Exp (₹ Cr)": _impact_agri_exp,
#     "Ind Exp (₹ Cr)": _impact_ind_exp,
#     "Serv Exp (₹ Cr)": _impact_serv_exp,
#     "Electrification (%)": _impact_electrification,
#     "Sanitation (%)": _impact_sanitation,
#     "Piped Water (%)": _impact_piped_water,
#     "HDI": _impact_hdi,
#     "SDG Index": _impact_sdg,
#     "IMR": _impact_imr,
#     "Life Expectancy": _impact_life_expectancy,
#     "Skill Coverage (%)": _impact_skill,
#     "Urban Housing Units (Lakh)": _impact_housing,
#     "Unemployment (%)": _impact_unemployment,
#     # Add other indicators here if needed
# }

# # ---------- Public function ----------
# def generate_impact_summary(state, df_full, input_indicator, outcome_indicator, target_lines=16):
#     """
#     Public interface used by app.py.
#     Focuses on 'outcome_indicator' (the KPI whose ground impact we want).
#     The 'input_indicator' is used optionally to mention pathways.
#     """
#     try:
#         # focus on outcome_indicator
#         focus = outcome_indicator
#         df_state = df_full[df_full["State"] == state].copy()
#         if df_state.empty:
#             return f"# Impact Report — {state}\n\nNo data available for this state."

#         # If we have a custom template
#         tpl = DISPATCH.get(focus)
#         if tpl is None:
#             # Generic fallback: show first→last + pathway if input provided
#             a,b,pct = _first_last(df_state, focus) if focus in df_state.columns else (None,None,None)
#             lines = [f"**Focus:** {focus}"]
#             if pct is not None:
#                 lines.append(f"- {focus} { _trend_word(pct) } ({pct:.1f}%).")
#             else:
#                 lines.append(f"- Trend for {focus} not computable.")
#             if input_indicator and input_indicator in df_state.columns:
#                 inp_pct = _first_last(df_state, input_indicator)[2]
#                 if inp_pct is not None:
#                     lines.append(f"- {input_indicator} changed by {inp_pct:.1f}% and may be a pathway affecting {focus}.")
#             # pad
#             while len(lines) < target_lines:
#                 lines.append("- Recommendation: gather outcome-specific ground metrics to validate impact.")
#             return "\n".join(lines[:target_lines])

#         lines = tpl(state, df_state, input_indicator, target_lines)
#         # include quick note on pathway if input is relevant and different from focus
#         if input_indicator and input_indicator != focus and input_indicator in df_state.columns:
#             inp_pct = _first_last(df_state, input_indicator)[2]
#             if inp_pct is not None:
#                 lines = [lines[0]] + [f"- (Pathway) {input_indicator} changed by {inp_pct:.1f}%; may influence {focus}."] + lines[1:]
#         # join and return
#         return "\n".join(lines[:target_lines])
#     except Exception as e:
#         return f"### Error generating indicator-specific impact summary: {e}"


import pandas as pd
import numpy as np
from .state_profiles import state_profiles

# ----------------- Small helpers -----------------

def _first_last(df_state, col):
    """Return (first, last, pct_change) for a column in a state's time series."""
    try:
        s = df_state[col].dropna()
        if s.empty:
            return None, None, None
        a = float(s.iloc[0])
        b = float(s.iloc[-1])
        pct = ((b - a) / a) * 100 if a != 0 else None
        return a, b, pct
    except Exception:
        return None, None, None

def _latest(df_state, col):
    """Return latest value for a column."""
    try:
        v = df_state[col].dropna().iloc[-1]
        return float(v)
    except Exception:
        return None

def _fmt(val, suffix=""):
    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
        return "N/A"
    try:
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return f"{val:,}{suffix}"
    except Exception:
        return str(val) + suffix

def _trend_word(pct):
    if pct is None:
        return "no clear trend"
    if pct > 20:
        return "strong increase"
    if pct > 5:
        return "moderate increase"
    if pct > -5:
        return "stable / marginal change"
    if pct > -20:
        return "moderate decline"
    return "sharp decline"


# ----------------- Indicator-specific impact blocks -----------------

def _impact_literacy(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Literacy (%)")
    edu_pct = _first_last(df_state, "Edu Exp (₹ Cr)")[2]
    skill_latest = _latest(df_state, "Skill Coverage (%)")
    pci_pct = _first_last(df_state, "Per Capita Income (₹)")[2]

    lines.append(f"### Ground impact: Literacy (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Literacy improved from **{a:.1f}%** to **{b:.1f}%** ({_trend_word(pct)}).")
    else:
        lines.append("- Literacy series is incomplete; trend cannot be computed reliably.")

    if edu_pct is not None:
        lines.append(f"- Education expenditure shows a **{_trend_word(edu_pct)}** (~{edu_pct:.1f}%), supporting expansion of schooling inputs (teachers, classrooms, textbooks).")
    if skill_latest is not None:
        lines.append(f"- Skill coverage (latest) is around **{_fmt(skill_latest, '%')}**, suggesting more youth are getting vocational/skill training beyond basic schooling.")
    if pci_pct is not None and pct is not None and pci_pct > 0 and pct > 0:
        lines.append("- Simultaneous gains in literacy and per-capita income point to better translation of education into earnings over time.")

    lines.append("- On-the-ground effects are likely: higher school completion, better access to formal sector jobs, and more informed health/financial decisions in households.")
    lines.append("- To validate impact, the state should track: learning outcomes (tests), dropout rates, gender gaps, and rural–urban gaps in literacy.")

    if input_indicator and input_indicator == "Edu Exp (₹ Cr)":
        lines.append("- The chosen input **Edu Exp (₹ Cr)** is directly linked to literacy via teacher recruitment, school infrastructure, and learning materials.")

    return lines


def _impact_pci(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Per Capita Income (₹)")
    p0, p1, ppct = _first_last(df_state, "Poverty (%)")
    gdp_pct = _first_last(df_state, "GSDP (₹ Cr)")[2]

    lines.append(f"### Ground impact: Per Capita Income (₹) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Per-capita income rose from **₹{a:,.0f}** to **₹{b:,.0f}** ({_trend_word(pct)}).")
    else:
        lines.append("- PCI series is incomplete; cannot compute start→latest change.")

    if gdp_pct is not None:
        lines.append(f"- Overall GSDP shows a **{_trend_word(gdp_pct)}** (~{gdp_pct:.1f}%), creating macroeconomic space for jobs and public spending.")
    if p0 is not None and p1 is not None:
        if ppct is not None and ppct < 0:
            lines.append(f"- Poverty has fallen from **{p0:.1f}%** to **{p1:.1f}%**, indicating that at least part of income growth has reached poorer households.")
        else:
            lines.append(f"- Poverty changed from **{p0:.1f}%** to **{p1:.1f}%**; depth and distribution of gains need closer examination.")

    lines.append("- On the ground, higher PCI usually reflects better wages, more regular employment, and stronger household consumption, especially in urban and semi-urban areas.")
    lines.append("- However, PCI is an average: inequality can still widen if high-income groups capture most of the gains. District-wise breakdowns are essential to see who benefited.")

    if input_indicator and input_indicator in df_state.columns and input_indicator != "Per Capita Income (₹)":
        inp_a, inp_b, inp_pct = _first_last(df_state, input_indicator)
        if inp_pct is not None:
            lines.append(f"- The selected input **{input_indicator}** changed by ~{inp_pct:.1f}%, which may have indirectly supported higher incomes (e.g., via productivity or human capital).")

    return lines


def _impact_gsdp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "GSDP (₹ Cr)")
    ind_pct = _first_last(df_state, "Ind Exp (₹ Cr)")[2]
    serv_pct = _first_last(df_state, "Serv Exp (₹ Cr)")[2]

    lines.append(f"### Ground impact: GSDP (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- GSDP expanded from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr**, indicating a **{_trend_word(pct)}** in overall output.")
    else:
        lines.append("- GSDP trend could not be reliably computed.")

    if ind_pct is not None or serv_pct is not None:
        lines.append("- Sectoral contribution signals:")
        if ind_pct is not None:
            lines.append(f"  - Industry-related spending changed **{_trend_word(ind_pct)}** (~{ind_pct:.1f}%), supporting manufacturing and construction activity.")
        if serv_pct is not None:
            lines.append(f"  - Services-related spending changed **{_trend_word(serv_pct)}** (~{serv_pct:.1f}%), driving services-led growth (IT, trade, logistics, finance).")

    lines.append("- On the ground, higher GSDP often shows up as more visible construction, expanded factories/services, increased traffic and commercial activity in growth hubs.")
    lines.append("- A key question for policy is whether this growth is broad-based (many districts benefiting) or concentrated in a few urban/industrial corridors.")

    return lines


def _impact_poverty(state, df_state, input_indicator):
    lines = []
    p0, p1, pct = _first_last(df_state, "Poverty (%)")
    pci_pct = _first_last(df_state, "Per Capita Income (₹)")[2]

    lines.append(f"### Ground impact: Poverty (%) in {state}")
    if p0 is not None and p1 is not None:
        if pct is not None and pct < 0:
            lines.append(f"- Poverty declined from **{p0:.1f}%** to **{p1:.1f}%**, showing a **{_trend_word(pct)}** in deprivation levels.")
        else:
            lines.append(f"- Poverty changed from **{p0:.1f}%** to **{p1:.1f}%**; net improvement is modest.")
    else:
        lines.append("- Poverty data series is incomplete; cannot accurately assess trend.")

    if pci_pct is not None:
        lines.append(f"- Per-capita income shows **{_trend_word(pci_pct)}** (~{pci_pct:.1f}%), which typically helps reduce poverty if growth is inclusive.")

    lines.append("- On the ground, poverty reduction should be visible as better food security, fewer distress migrations, and more resilient consumption during shocks.")
    lines.append("- To verify, one should look at social protection coverage (PDS, cash transfers), MGNREGA demand, and share of vulnerable households in each district.")

    return lines


def _impact_urbanization(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Urbanization (%)")
    housing_latest = _latest(df_state, "Urban Housing Units (Lakh)")

    lines.append(f"### Ground impact: Urbanization (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Urbanization increased from **{a:.1f}%** to **{b:.1f}%** ({_trend_word(pct)}), indicating more people living in urban areas.")
    else:
        lines.append("- Urbanization trend cannot be precisely computed from the data.")

    if housing_latest is not None:
        lines.append(f"- Urban housing stock stands at around **{_fmt(housing_latest)} Lakh units**, which must keep pace with migration to avoid overcrowding and informal settlements.")

    lines.append("- On the ground, rising urbanization is seen through city expansion, new peri-urban clusters, rising land prices, and heavier pressure on water, transport and waste systems.")
    lines.append("- Policy focus should be on managing planned growth: affordable housing, public transport, and slum-upgrading to avoid long-term inequality traps.")

    return lines


def _impact_edu_exp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Edu Exp (₹ Cr)")
    lit_pct = _first_last(df_state, "Literacy (%)")[2]

    lines.append(f"### Ground impact: Edu Exp (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Education expenditure rose from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr**, a **{_trend_word(pct)}** over the period.")
    else:
        lines.append("- Education expenditure series is incomplete; trend unclear.")

    if lit_pct is not None:
        lines.append(f"- Literacy levels show a **{_trend_word(lit_pct)}** (~{lit_pct:.1f}%), suggesting some conversion of spending into learning/attainment.")
    lines.append("- Ground impact is seen in classroom infrastructure, teacher availability, enrollment and retention, and exam performance of students.")
    lines.append("- The quality of spending (teacher training, remedial education, early-grade reading) is often more important than raw budget levels.")

    return lines


def _impact_health_exp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Health Exp (₹ Cr)")
    imr_latest = _latest(df_state, "IMR")
    life_latest = _latest(df_state, "Life Expectancy")

    lines.append(f"### Ground impact: Health Exp (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Health expenditure increased from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr** ({_trend_word(pct)}).")
    else:
        lines.append("- Health spending trend cannot be reliably computed.")

    if imr_latest is not None:
        lines.append(f"- Latest Infant Mortality Rate (IMR) is around **{_fmt(imr_latest)} per 1000 births**, capturing neonatal and maternal care quality.")
    if life_latest is not None:
        lines.append(f"- Life expectancy is about **{_fmt(life_latest)} years**, reflecting long-run health, nutrition and safety conditions.")

    lines.append("- On-the-ground, higher health spending should show up as stronger primary care, better-equipped hospitals, higher immunization, and shorter travel time for patients.")
    lines.append("- To validate impact, one must track service coverage (ANC visits, institutional deliveries, screening programs) and disaggregated IMR/MMR trends.")

    return lines


def _impact_agri_exp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Agri Exp (₹ Cr)")

    lines.append(f"### Ground impact: Agri Exp (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Agriculture expenditure moved from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr** ({_trend_word(pct)}).")
    else:
        lines.append("- Agriculture expenditure series is not sufficient to compute trends.")

    lines.append("- On farms, this spending typically finances irrigation projects, input support, extension services and price interventions.")
    lines.append("- Visible field-level outcomes: more irrigated area, improved yields, reduced distress cropping patterns, and better resilience to rainfall shocks.")

    return lines


def _impact_ind_exp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Ind Exp (₹ Cr)")

    lines.append(f"### Ground impact: Ind Exp (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Industrial expenditure increased from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr** ({_trend_word(pct)}).")
    else:
        lines.append("- Industrial expenditure trend cannot be computed cleanly.")

    lines.append("- Ground impact channel: manufacturing and construction projects that create jobs, expand supply chains, and demand for logistics and services.")
    lines.append("- Whether this translates into inclusive benefits depends on MSME participation, labour conditions, and geographic spread of new plants/projects.")

    return lines


def _impact_serv_exp(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Serv Exp (₹ Cr)")

    lines.append(f"### Ground impact: Serv Exp (₹ Cr) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Services expenditure rose from **₹{a:,.0f} Cr** to **₹{b:,.0f} Cr** ({_trend_word(pct)}).")
    else:
        lines.append("- Services expenditure series insufficient for a robust trend.")

    lines.append("- On the ground, this supports growth in trade, IT, finance, tourism and other services, often concentrated in urban centers.")
    lines.append("- It typically shows up as more office towers, retail hubs, business parks and tourism infrastructure, with associated employment shifts.")

    return lines


def _impact_electrification(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Electrification (%)")

    lines.append(f"### Ground impact: Electrification (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Electrification improved from **{a:.1f}%** to **{b:.1f}%**, a **{_trend_word(pct)}** in household connections.")
    else:
        lines.append("- Electrification series is incomplete; cannot compute trend.")

    lines.append("- On the ground, near-universal electrification changes daily life: extended study hours, better lighting, refrigeration, and small-enterprise productivity.")
    lines.append("- The real test is not just connections but reliability: hours of supply, voltage stability, and affordability.")

    return lines


def _impact_sanitation(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Sanitation (%)")

    lines.append(f"### Ground impact: Sanitation (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Sanitation coverage increased from **{a:.1f}%** to **{b:.1f}%** ({_trend_word(pct)}).")
    else:
        lines.append("- Sanitation coverage trend is not fully measurable from data.")

    lines.append("- On-the-ground impact: reduced open defecation, better dignity (especially for women), and lower incidence of diarrhoeal diseases and worm infections.")
    lines.append("- Behaviour-change and maintenance practices are critical to sustain these gains beyond infrastructure rollout.")

    return lines


def _impact_piped_water(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Piped Water (%)")

    lines.append(f"### Ground impact: Piped Water (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Piped water access expanded from **{a:.1f}%** to **{b:.1f}%**, showing a **{_trend_word(pct)}** in household tap connections.")
    else:
        lines.append("- Piped water data is incomplete; cannot compute trend.")

    lines.append("- On-the-ground, this reduces time spent collecting water, improves hygiene and makes daily chores less labour-intensive, especially for women and children.")
    lines.append("- Water quality and continuity of supply determine whether health indicators actually improve.")

    return lines


def _impact_hdi(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "HDI")

    lines.append(f"### Ground impact: HDI in {state}")
    if a is not None and b is not None:
        lines.append(f"- HDI improved from **{a:.2f}** to **{b:.2f}** ({_trend_word(pct)}).")
    else:
        lines.append("- HDI trend cannot be reliably computed from data.")

    lines.append("- HDI summarizes health, education and income; ground impact appears as better schooling, longer lives and higher living standards on average.")
    lines.append("- Disaggregating HDI by district/region is important to catch pockets of low development within the state.")

    return lines


def _impact_sdg(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "SDG Index")

    lines.append(f"### Ground impact: SDG Index in {state}")
    if a is not None and b is not None:
        lines.append(f"- SDG Index moved from **{a:.1f}** to **{b:.1f}** ({_trend_word(pct)} in multi-dimensional development).")
    else:
        lines.append("- SDG Index series not sufficient for a trend.")

    lines.append("- On the ground this captures improvements across poverty, health, education, gender, climate, institutions and more.")
    lines.append("- For operational impact, break down which SDG goals are lagging and align schemes accordingly.")

    return lines


def _impact_imr(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "IMR")

    lines.append(f"### Ground impact: IMR in {state}")
    if a is not None and b is not None:
        lines.append(f"- IMR changed from **{_fmt(a)}** to **{_fmt(b)}** per 1000 births ({_trend_word(pct)}).")
    else:
        lines.append("- IMR trend cannot be robustly estimated.")

    lines.append("- Ground impact is directly tied to newborn and maternal survival; it reflects immunization, ANC coverage, institutional delivery and neonatal care.")
    lines.append("- Facility-level strengthening and community health workers are usually key drivers of sustained IMR decline.")

    return lines


def _impact_life_expectancy(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Life Expectancy")

    lines.append(f"### Ground impact: Life Expectancy in {state}")
    if a is not None and b is not None:
        lines.append(f"- Life expectancy increased from **{_fmt(a)}** to **{_fmt(b)}** years ({_trend_word(pct)}).")
    else:
        lines.append("- Life expectancy trend not fully measurable from data.")

    lines.append("- Higher life expectancy generally reflects improvements in nutrition, public health, healthcare access, and road safety.")
    lines.append("- It is a long-run outcome; short-term shocks (epidemics, disasters) may temporarily dent progress.")

    return lines


def _impact_skill(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Skill Coverage (%)")

    lines.append(f"### Ground impact: Skill Coverage (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Skill coverage moved from **{a:.1f}%** to **{b:.1f}%** ({_trend_word(pct)}).")
    else:
        lines.append("- Skill coverage trend is not completely available.")

    lines.append("- On the ground this should translate into better employability, especially for youth and those transitioning from informal to formal jobs.")
    lines.append("- Placement rates, wage gains for trained candidates, and employer feedback are critical to validate impact.")

    return lines


def _impact_housing(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Urban Housing Units (Lakh)")

    lines.append(f"### Ground impact: Urban Housing Units (Lakh) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Urban housing stock expanded from **{_fmt(a)} Lakh** to **{_fmt(b)} Lakh** ({_trend_word(pct)}).")
    else:
        lines.append("- Urban housing series insufficient for a clear trend.")

    lines.append("- On-the-ground, this can mean new layouts, apartment complexes and regularized colonies, but affordability and service access (water, roads) must be tracked.")
    lines.append("- Policy questions: who is getting housed (EWS/MIG/HIG), and where (central city vs peri-urban fringe).")

    return lines


def _impact_unemployment(state, df_state, input_indicator):
    lines = []
    a, b, pct = _first_last(df_state, "Unemployment (%)")

    lines.append(f"### Ground impact: Unemployment (%) in {state}")
    if a is not None and b is not None:
        lines.append(f"- Unemployment changed from **{a:.1f}%** to **{b:.1f}%** ({_trend_word(pct)}).")
    else:
        lines.append("- Unemployment series is incomplete; trend not clear.")

    lines.append("- On the ground this reflects difficulty in finding suitable jobs, especially for youth and educated workers.")
    lines.append("- It interacts with migration (to cities, to other states), informality, and the success of skill programs.")

    return lines


# ----------------- Dispatcher -----------------

DISPATCH = {
    "Literacy (%)": _impact_literacy,
    "Per Capita Income (₹)": _impact_pci,
    "GSDP (₹ Cr)": _impact_gsdp,
    "Poverty (%)": _impact_poverty,
    "Urbanization (%)": _impact_urbanization,
    "Edu Exp (₹ Cr)": _impact_edu_exp,
    "Health Exp (₹ Cr)": _impact_health_exp,
    "Agri Exp (₹ Cr)": _impact_agri_exp,
    "Ind Exp (₹ Cr)": _impact_ind_exp,
    "Serv Exp (₹ Cr)": _impact_serv_exp,
    "Electrification (%)": _impact_electrification,
    "Sanitation (%)": _impact_sanitation,
    "Piped Water (%)": _impact_piped_water,
    "HDI": _impact_hdi,
    "SDG Index": _impact_sdg,
    "IMR": _impact_imr,
    "Life Expectancy": _impact_life_expectancy,
    "Skill Coverage (%)": _impact_skill,
    "Urban Housing Units (Lakh)": _impact_housing,
    "Unemployment (%)": _impact_unemployment,
}


# ----------------- Public API used by app.py -----------------

def generate_impact_summary(state, df_full, input_indicator, outcome_indicator, target_lines=None):
    """
    Focuses on the OUTCOME indicator (selected_outcome in your dashboard).
    Input indicator is only mentioned as a possible pathway, not the main focus.
    """
    try:
        df_state = df_full[df_full["State"] == state].copy()
        if df_state.empty:
            return f"### Impact report\n\nNo data available for {state}."

        focus = outcome_indicator
        func = DISPATCH.get(focus)

        # If we don't have a custom template, fall back to generic
        if func is None:
            a, b, pct = _first_last(df_state, focus) if focus in df_state.columns else (None, None, None)
            lines = [f"### Ground impact: {focus} in {state}"]
            if a is not None and b is not None:
                lines.append(f"- {focus} changed from **{_fmt(a)}** to **{_fmt(b)}** ({_trend_word(pct)}).")
            else:
                lines.append(f"- Data for {focus} is not sufficient to compute a trend.")
            if input_indicator and input_indicator in df_state.columns and input_indicator != focus:
                ia, ib, ipct = _first_last(df_state, input_indicator)
                if ipct is not None:
                    lines.append(f"- The selected input **{input_indicator}** changed by roughly {ipct:.1f}%, and may influence {focus}.")
            return "\n".join(lines)

        lines = func(state, df_state, input_indicator)

        # If input_indicator is a plausible driver and different from focus, add one concise line near top
        if input_indicator and input_indicator != focus and input_indicator in df_state.columns:
            ia, ib, ipct = _first_last(df_state, input_indicator)
            if ipct is not None:
                # insert after title line
                lines.insert(1, f"- The selected input **{input_indicator}** changed by about **{ipct:.1f}%**, and can act as a driver for this outcome.")

        return "\n".join(lines)

    except Exception as e:
        return f"### Error generating impact summary: {e}"
