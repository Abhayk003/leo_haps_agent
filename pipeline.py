from agent import run_agent, extract_plan
from agent_tools import evaluate_plan
from goal_checker import check_goal


def run_pipeline(goal, budget):
    issues = check_goal(goal)
    limitations = [f"{item['category']}: {item['reason']}" for item in issues]

    answer, calls = run_agent(goal, budget, verbose=False)

    for name, args in calls:
        if name == "build_plan":
            try:
                requested = int(args["max_haps_minutes"])
            except (KeyError, ValueError):
                continue
            if requested > budget:
                limitations.append(f"budget: the goal asks for {requested} HAPS minutes "
                                   f"but the budget is {budget}.")
                break

    plan = extract_plan(answer)
    if plan is None:
        verified = "invalid answer (no single FINAL PLAN line)"
    else:
        verified = evaluate_plan(plan)

    return {"limitations": limitations, "plan": plan, "verified": verified,
            "answer": answer, "calls": calls}