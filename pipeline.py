import agent_tools
from agent import run_agent, extract_plan
from agent_tools import verify_plan, set_planning_data, set_reserve, set_true_data
from goal_checker import check_goal, extract_reserve

FORECAST_NOTE = "Note: rain timing comes from a weather forecast, which may be wrong."


def run_pipeline(goal, budget, planning_file="scenario_links.csv", true_file="scenario_links.csv"):
    set_true_data(true_file)
    if planning_file == true_file:
        set_planning_data(planning_file)
    else:
        set_planning_data(planning_file, FORECAST_NOTE)

    issues = check_goal(goal)
    limitations = [f"{item['category']}: {item['reason']}" for item in issues]

    reserve = extract_reserve(goal)
    set_reserve(reserve)

    answer, calls = run_agent(goal, budget, verbose=False)

    cap = budget
    over_budget_request = None
    for name, args in calls:
        if name != "build_plan":
            continue
        try:
            requested = int(args["max_haps_minutes"])
        except (KeyError, ValueError):
            continue
        cap = min(requested, budget)
        if requested > budget:
            over_budget_request = requested
    if over_budget_request is not None:
        limitations.append(f"budget: the goal asks for {over_budget_request} HAPS minutes "
                           f"but the budget is {budget}.")
    dead = sum(1 for t in agent_tools.OPTIONS if agent_tools.haps_gain(t)[1] == 0.0)
    if dead > cap:
        limitations.append(f"outages: about {dead} minutes are predicted to have no usable LEO "
                           f"link, more than the {cap} HAPS minutes allowed, so some outages "
                           f"cannot be avoided.")

    plan = extract_plan(answer)
    if plan is None:
        verified = "invalid answer (no single FINAL PLAN line)"
    else:
        s = verify_plan(plan, cap)
        verified = (f"HAPS minutes used: {s['haps_min']} of {cap}\n"
                    f"Outage minutes: {s['outage_min']}\n"
                    f"Average throughput: {s['avg_throughput_mbps']:.1f} Mbps\n"
                    f"Handovers: {s['handovers']}")

    return {"limitations": limitations, "plan": plan, "verified": verified,
            "answer": answer, "calls": calls, "reserve": reserve}