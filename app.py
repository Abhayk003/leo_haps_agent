import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from pipeline import run_pipeline
from link_model import leo_link, haps_link
from simulator import load_options, run, usable_capacity
from policies import (best_leo, leo_only, greedy_with_budget, haps_as_fallback,
                      make_perfect_planner, make_hybrid_planner)

EARTH_RADIUS_KM = 6371.0
HAPS_ELEV_DEG = 45.0
SIZES = {
    "25% of OneWeb (162 satellites)": ("scenario_links_25.csv", "scenario_links_forecast_25.csv"),
    "15% of OneWeb (97 satellites)": ("scenario_links.csv", "scenario_links_forecast.csv"),
    "10% of OneWeb (65 satellites)": ("scenario_links_10.csv", "scenario_links_forecast_10.csv"),
}


@st.cache_data
def cached_options(path):
    return load_options(path)


def dead_minutes(options):
    count = 0
    for opts in options.values():
        leo = best_leo(opts)
        if leo is None or usable_capacity(leo) == 0.0:
            count += 1
    return count


def bar_chart(df, column, title):
    order = list(df["Policy"])
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(field=column, type="quantitative", title=title, scale=alt.Scale(zero=True)),
            y=alt.Y(field="Policy", type="nominal", sort=order, title=None,
                    axis=alt.Axis(labelLimit=320)),
            color=alt.Color(field="Policy", type="nominal", sort=order, legend=None),
            tooltip=[alt.Tooltip(field="Policy", type="nominal"),
                     alt.Tooltip(field=column, type="quantitative")],
        )
        .properties(width="container", height=260)
    )

def slant_range_km(elev_deg, altitude_km):
    e = np.radians(elev_deg)
    r = EARTH_RADIUS_KM
    return float(np.sqrt((r + altitude_km) ** 2 - (r * np.cos(e)) ** 2) - r * np.sin(e))


st.set_page_config(page_title="LEO + HAPS Link Planner", page_icon="🛰️", layout="wide")
st.title("🛰️ LEO + HAPS Link Planner")
st.caption("User at RVCE, Bengaluru · built with Skyfield, ITU-Rpy and a local Qwen 2.5 model")

tab_link, tab_policies, tab_agent = st.tabs(["📡 Link calculator", "📊 HAPS policies", "🤖 AI planner"])

with tab_link:
    st.subheader("How does the elevation angle change the LEO link?")
    col_in, col_out = st.columns([1, 2])

    with col_in:
        elev = st.slider("Satellite elevation angle (degrees)", 10, 89, 45)
        altitude = st.slider("Satellite altitude (km)", 400.0, 1300.0, 482.5, step=0.5)
        raining = st.toggle("Heavy rain (exceeded 0.1% of the year)")

    dist = slant_range_km(elev, altitude)
    leo = leo_link(elev, dist, raining=raining)
    haps = haps_link(HAPS_ELEV_DEG, raining=raining)

    with col_out:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distance", f"{dist:,.0f} km")
        c2.metric("SNR", f"{leo['snr_db']:.1f} dB")
        c3.metric("Capacity (Mbps)", f"{leo['capacity_mbps']:,.0f}")
        c4.metric("Delay", f"{leo['delay_ms']:.2f} ms")

        if leo["snr_db"] < 0:
            st.error("LEO link unusable: SNR is below 0 dB.")
        else:
            st.success("LEO link usable.")

        st.markdown(f"**For comparison, HAPS at {HAPS_ELEV_DEG:.0f}° elevation:** "
                    f"SNR {haps['snr_db']:.1f} dB · capacity {haps['capacity_mbps']:,.0f} Mbps · "
                    f"delay {haps['delay_ms']:.3f} ms")
        if haps["capacity_mbps"] > leo["capacity_mbps"]:
            st.info("HAPS is faster than this LEO link right now.")
        else:
            st.info("This LEO link is faster than HAPS.")

with tab_policies:
    st.subheader("How should a limited HAPS budget be spent?")
    col_in, col_out = st.columns([1, 2])

    with col_in:
        size = st.selectbox("Constellation size", list(SIZES), index=1)
        budget = st.slider("HAPS budget (minutes out of 181)", 0, 36, 15)
        reserve = st.slider("Reserve for forecast errors (minutes)", 0, 9, 3)
        st.caption("Real rain: minutes 60 to 119. Forecast used for planning: 50 to 109 (10 minutes early).")

    true_file, forecast_file = SIZES[size]
    truth = cached_options(true_file)
    forecast = cached_options(forecast_file)

    policies = {
        "LEO only": leo_only,
        "Greedy with budget": greedy_with_budget,
        "HAPS as fallback": haps_as_fallback,
        "Planner on forecast": make_perfect_planner(forecast, budget),
        f"Hybrid, reserve {reserve}": make_hybrid_planner(forecast, budget, reserve),
        "Perfect planner (knows real weather)": make_perfect_planner(truth, budget),
    }

    rows = []
    for name, policy in policies.items():
        s = run(policy, truth, budget=budget)
        rows.append({"Policy": name,
                     "Throughput (Mbps)": round(s["avg_throughput_mbps"], 1),
                     "Outage minutes": s["outage_min"],
                     "HAPS minutes used": s["haps_min"],
                     "Handovers": s["handovers"]})
    df = pd.DataFrame(rows)
    df["Gain over LEO only (Mbps)"] = (df["Throughput (Mbps)"] - df["Throughput (Mbps)"].iloc[0]).round(1)

    with col_out:
        dead = dead_minutes(truth)
        if dead > budget:
            st.warning(f"{dead} minutes have no usable satellite, more than the {budget}-minute budget, "
                       f"so at least {dead - budget} outage minutes are unavoidable.")

        realistic = df[~df["Policy"].str.startswith("Perfect")]
        best = realistic.sort_values(["Outage minutes", "Throughput (Mbps)"], ascending=[True, False]).iloc[0]
        st.success(f"Best realistic policy: **{best['Policy']}**, {best['Throughput (Mbps)']} Mbps "
                   f"with {best['Outage minutes']} outage minutes.")

        st.dataframe(df, hide_index=True)

        chart_left, chart_right = st.columns(2)
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.altair_chart(bar_chart(df, "Gain over LEO only (Mbps)", "Throughput gain over LEO only (Mbps)"))
        with chart_right:
            st.altair_chart(bar_chart(df, "Outage minutes", "Outage minutes"))

with tab_agent:
    st.subheader("Plan HAPS use from a goal in plain English")
    col_in, col_out = st.columns([1, 2])

    with col_in:
        goal = st.text_area("Operator goal",
                            "Avoid all outages first. Then make the average throughput as high as possible.",
                            height=120)
        size_a = st.selectbox("Constellation size", list(SIZES), index=1, key="agent_size")
        budget_a = st.slider("HAPS budget (minutes out of 181)", 1, 36, 15, key="agent_budget")
        use_forecast = st.toggle("Plan with the weather forecast (it may be wrong)", key="agent_forecast")
        st.caption("Goals to try: \"HAPS should be an emergency backup only.\" · "
                   "\"Keep 7 HAPS minutes in reserve for other users.\" · "
                   "\"The rain forecast may be wrong, so keep some HAPS minutes ready for surprises.\" · "
                   "\"Keep the number of handovers below 30.\"")
        clicked = st.button("Make a plan", type="primary")

    if clicked:
        if not goal.strip():
            st.warning("Type a goal first.")
        else:
            true_file, forecast_file = SIZES[size_a]
            planning_file = forecast_file if use_forecast else true_file
            with st.spinner("The agent is planning... this can take up to a minute."):
                try:
                    st.session_state["agent_result"] = run_pipeline(
                        goal, budget_a, planning_file=planning_file, true_file=true_file)
                    st.session_state["agent_inputs"] = (goal, size_a, budget_a, use_forecast)
                except Exception as e:
                    st.session_state["agent_result"] = None
                    st.error(f"The planner failed: {e}. Is Ollama running?")

    r = st.session_state.get("agent_result")
    with col_out:
        if r is None:
            st.info("Type a goal and click **Make a plan**.")
        else:
            g, s_label, b, fc = st.session_state["agent_inputs"]
            st.caption(f"Goal: \"{g}\" · {s_label} · budget {b} min · "
                       f"planned with {'the forecast' if fc else 'real weather'}")

            if r["limitations"]:
                for lim in r["limitations"]:
                    st.warning(f"Limitation: {lim}")
            else:
                st.success("Every part of this goal can be handled.")

            settings = None
            for name, args in r["calls"]:
                if name == "build_plan":
                    settings = args
            st.markdown("**Settings chosen by the agent**")
            s1, s2, s3, s4 = st.columns(4)
            if settings:
                s1.metric("Max HAPS minutes", str(settings.get("max_haps_minutes", "?")))
                s2.metric("Min gain (Mbps)", str(settings.get("min_gain_mbps", "?")))
                s3.metric("Minimise HAPS use", str(settings.get("minimise_haps_use", "?")))
            s4.metric("Reserve minutes", str(r["reserve"]))

            if r["plan"] is None:
                st.error("The agent did not give a valid final plan.")
            else:
                st.markdown(f"**Planned HAPS minutes:** {r['plan']}")
                values = dict(line.split(": ", 1) for line in r["verified"].splitlines())
                st.markdown("**Verified result** (re-simulated on real weather)")
                v1, v2, v3, v4 = st.columns(4)
                v1.metric("Throughput (Mbps)", values["Average throughput"].replace(" Mbps", ""))
                v2.metric("Outage minutes", values["Outage minutes"])
                v3.metric("HAPS minutes used", values["HAPS minutes used"])
                v4.metric("Handovers", values["Handovers"])

            with st.expander("Agent's explanation"):
                st.write(r["answer"])
            with st.expander("Tool calls made by the agent"):
                for name, args in r["calls"]:
                    st.code(f"{name}({args})")