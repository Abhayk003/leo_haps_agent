from agent import run_agent, extract_plan
from agent_tools import evaluate_plan

BUDGET = 15

GOALS = [
    "Keep the number of handovers below 30.",
    "Always choose the link with the lowest delay.",
    "Use HAPS only between minute 100 and minute 130.",
    "Make sure there are no outages and use exactly 20 HAPS minutes.",
]

for i, goal in enumerate(GOALS, start=1):
    answer, calls = run_agent(goal, BUDGET, verbose=False)

    print(f"=== Goal {i}: {goal}")
    print("Tools called:")
    for name, args in calls:
        print(f"  {name}({args})")
    print("Agent's answer:")
    print(answer)
    print(f"  LIMITATION line written: {'yes' if 'LIMITATION:' in answer else 'no'}")
    
    plan = extract_plan(answer)
    print("Verified result:")
    if plan is None:
        print("  invalid answer (no single FINAL PLAN line)")
    else:
        for line in evaluate_plan(plan).splitlines():
            print(f"  {line}")
    print()