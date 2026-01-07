


import pandas as pd
import numpy as np
from utils import safe_corr
from state_profiles import state_profiles




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
