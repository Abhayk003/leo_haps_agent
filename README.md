# LEO + HAPS Link Planner

**Performance analysis of LEO satellite links at different elevation angles with High Altitude Platform Station (HAPS) support and an agentic AI planner.**

College project, RV College of Engineering (RVCE), Bengaluru. Author: Abhay Kulkarni.

Everything runs on free, open tools: Python, Skyfield, ITU-Rpy and a local language model (Qwen 2.5) through Ollama. No paid software or API is needed.

---

## What this project does

A user at RVCE connects to the internet through LEO satellites (Starlink / OneWeb). A satellite low in the sky is farther away and its signal crosses more rain, so the link weakens. A HAPS (an aircraft or balloon about 20 km up) can help, but its time is shared and limited.

The project answers three questions:

1. **How does link quality change with elevation angle?** Real orbit data plus ITU-R rain and gas models give SNR, capacity and delay at every angle.
2. **When is HAPS actually needed?** With full constellations, almost never; it matters when the constellation is sparse.
3. **How should a limited HAPS budget be spent?** Simple rules, a planner and an AI agent are compared, including when the weather forecast is wrong.

### Innovation

A **goal-driven HAPS planner**: an operator types a goal in plain English (for example *"use HAPS as little as possible, but never allow an outage"*). A local language model only translates the goal into three planner settings. Verified tools build the plan, and code re-checks every result on real weather. The model never does the arithmetic, so its known weaknesses (misreading numbers, inventing results) cannot corrupt the plan. Unsupported goals are reported honestly instead of being faked.

### Key results

| Finding | Number |
| --- | --- |
| SNR loss from 72° to 10° elevation | 10.7 dB (clear sky), 24.6 dB (heavy rain) |
| Capacity at 10° in heavy rain | 114 Mbps (vs 1,688 Mbps at 72°) |
| Lowest best-satellite elevation, full Starlink / full OneWeb | 64.4° / 48.1° |
| Outages, 15-minute HAPS budget: greedy vs planner | 6 vs 0 |
| Reserve that removed all outages under 5 forecast errors | 3 minutes |
| Agent settings correct (3 constellation sizes) | 20 of 21 tests |

The full report (methods, figures, tables, limitations) is provided separately.

---

## Repository structure

| File or folder | Purpose |
| --- | --- |
| `app.py` | **Interactive web app** (Streamlit): link calculator, policy comparison, AI planner |
| `link_model.py` | Link budgets for LEO and HAPS: path loss, ITU-R attenuation, SNR, capacity, delay |
| `simulator.py` | Minute-by-minute simulator: handovers, outages, HAPS budget |
| `policies.py` | All link-selection policies: LEO only, greedy, fallback, perfect planner, hybrid with reserve |
| `agent_tools.py` | Tools the AI agent can call: scenario summary, `build_plan`, `evaluate_plan`; plus final verification |
| `agent.py` | The AI agent (Qwen 2.5 7b with tool calling) |
| `goal_checker.py` | Separate model calls: unsupported-goal checker and reserve extractor |
| `pipeline.py` | Full pipeline: checker + reserve + agent + code checks + verification |
| `starlink.tle`, `oneweb.tle` | Saved satellite orbit data (CelesTrak, 2026-10-20) |
| `scenario_*.csv` | Saved scenarios: 15% (`scenario_links.csv`), 25% (`_25`), 10% (`_10`), real and forecast weather |
| `figures/` | Report figures and Table 4 |
| `elevation_analysis.png` | Figure 1: link performance vs elevation |
| `step*.py`, `test_*.py` | The step-by-step development scripts, numbered in the order they were built |
| `fig*.py`, `table4_forecast.py` | Scripts that produce the report figures and tables |

### The development scripts, by part

| Part | Scripts |
| --- | --- |
| A. Elevation analysis | `step2` to `step10`, `test_link_model.py`, `test_haps.py` |
| B. When HAPS is needed | `step12` to `step16`, `fig2_density.py` |
| C. Scenarios and policies | `step17`, `step18`, `step19` to `step22`, `step45` to `step47`, `step55`, `step56`, `fig3_budget_sweep.py`, `table4_forecast.py`, `fig5_sizes.py` |
| D. AI agent | `step24`, `step25`, `step36`, `step38`, `step44`, `step49`, `step50`, `step52`, `step57` |

---

## Requirements

- **Windows, Linux or macOS** (developed on Windows 11)
- **Python 3.10 or newer** (developed with Python 3.10)
- **Git**
- **Ollama** (free, from [ollama.com](https://ollama.com)), version 0.40.7 used
- About **6 GB of free disk space** for the language model
- A graphics card is optional; without one, the AI planner is slower

---

## Setup

### 1. Get the code

```
git clone https://github.com/Abhayk003/leo_haps_agent.git
cd leo_haps_agent
```

### 2. Create and activate a virtual environment

Windows (Command Prompt or PowerShell):
```
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:
```
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now start with `(venv)`.

If PowerShell says *"running scripts is disabled on this system"*, run this once and try again:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3. Install the Python packages

```
pip install -r requirements.txt
```

### 4. Install Ollama and the model

Install Ollama from [ollama.com](https://ollama.com), start it, then download the model (about 4.7 GB):
```
ollama pull qwen2.5:7b
```

Check it works:
```
ollama run qwen2.5:7b "Say hello in one sentence."
```

Steps 1 to 3 are enough for everything except the AI planner. Only the agent needs Ollama.

---

## Run the app

Make sure Ollama is running, then:
```
streamlit run app.py
```

It opens at **http://localhost:8501**. Stop it with **Ctrl+C** in the terminal.

| Tab | Try this |
| --- | --- |
| **Link calculator** | Elevation 72 with no rain (about 2,030 Mbps), then elevation 10 with heavy rain (about −4.3 dB, link unusable) |
| **HAPS policies** | Default settings: greedy has 6 outages, the hybrid with a 3-minute reserve has 0. Then select 10% to see unavoidable outages |
| **AI planner** | Type a goal and click **Make a plan** (takes several seconds) |

Example goals for the AI planner:

| Goal | Forecast | Expected |
| --- | --- | --- |
| Avoid all outages first. Then make the average throughput as high as possible. | off | 984.3 Mbps, 0 outages |
| Use HAPS as little as possible, but never allow an outage. | off | only 6 HAPS minutes |
| Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput. | off | at most 8 HAPS minutes |
| Avoid all outages first. Then make the average throughput as high as possible. | on | 3 outages (the forecast misleads the plan) |
| Same goal + "The rain forecast may be wrong, so keep some HAPS minutes ready for surprises." | on | reserve 3, 0 outages |
| Keep the number of handovers below 30. | any | flagged as unsupported |

---

## Reproduce the main results

Run these from the project folder with `(venv)` active. They use the saved data files, so the numbers match the report.

| Command | What it reproduces | Expected |
| --- | --- | --- |
| `python step10_plot_elevation.py` | Figure 1, elevation analysis | Check line: slant range at 10° ≈ 1651.4 km |
| `python step22_planner_sweep.py` | Budget sweep, greedy vs fallback vs planner | Budget 15: 958.8 / 6, 974.8 / 0, 984.3 / 0 |
| `python fig3_budget_sweep.py` | Figure 3 | Saves `figures/fig3_budget_sweep.png` |
| `python agent_tools.py` | Planner tool and forecast reserve | 984.3; then reserves 0/3/6/9: 965.1/3, 975.7/0, 976.4/0, 976.4/0 |
| `python table4_forecast.py` | Table 4, forecast errors vs reserve | Saves `figures/table4_forecast.csv` |
| `python step56_sizes.py` | Policies at 25%, 15% and 10% | 15% block matches the row above |
| `python step36_goal_suite.py` | Agent on 7 goals (needs Ollama) | Settings correct for 7 of 7 goals |
| `python step44_pipeline_test.py` | Full pipeline on 11 goals (needs Ollama) | Limitations on goals 8 to 11 |

### Important: do not overwrite the saved data

Some early scripts use the **current time** or **live CelesTrak data**. Running them creates new scenarios with different numbers and **overwrites** the saved files:

- `step17_make_scenario.py` overwrites `scenario_leo.csv`
- `step18_link_table.py` overwrites `scenario_links.csv`
- `step45_forecast_table.py` overwrites `scenario_links_forecast.csv`

Run them only if you want a fresh scenario. To get the original files back:
```
git restore scenario_leo.csv scenario_links.csv scenario_links_forecast.csv
```

`step55_make_scenarios.py` uses a fixed start time (2026-10-20 08:55:10 UTC), so it reproduces the 25% and 10% files exactly.

---

## Main assumptions

| Item | Value |
| --- | --- |
| User location | RVCE, Bengaluru (12.9237° N, 77.4987° E) |
| LEO downlink | 12 GHz, 250 MHz, EIRP 36 dBW, 0.5 m dish, 150 K |
| HAPS downlink | 20 km altitude at 45° elevation, 2.6 GHz, 100 MHz, EIRP 30 dBW |
| Heavy rain | ITU-R, exceeded 0.1% of the year; real rain at minutes 60 to 119 |
| Forecast (main case) | Rain at minutes 50 to 109 (10 minutes early) |
| Simulation | 181 one-minute steps, 2 s per handover, link unusable below 0 dB SNR |
| HAPS budget | 15 minutes per user (also swept 0 to 36) |
| Agent | Qwen 2.5 7b, temperature 0 |

Link parameters are representative assumptions, since Starlink and OneWeb do not publish exact values. The report discusses all limitations.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError` | The virtual environment is not active. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` |
| App says "The planner failed ... Is Ollama running?" | Start Ollama, wait a few seconds, click **Make a plan** again |
| `CUDA error` or `llama-server process has terminated` | Quit Ollama from the system tray, start it again. If it keeps happening, restart the computer or update the graphics driver |
| `upgrade in progress` from Ollama | Ollama is updating itself. Wait a few minutes |
| AI planner is very slow | Normal without a graphics card. Each plan can take a minute or more |
| An unusual goal gets an odd setting | A known limitation: the agent relies on fairly explicit wording |

---

## Tools and data

- [Skyfield](https://rhodesmill.org/skyfield/) for satellite positions
- [CelesTrak](https://celestrak.org) for orbit data
- [ITU-Rpy](https://github.com/inigodelportillo/ITU-Rpy) for ITU-R propagation models
- [Ollama](https://ollama.com) with [Qwen 2.5](https://ollama.com/library/qwen2.5)
- [Streamlit](https://streamlit.io) for the web app
