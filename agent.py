import re
import ollama
import agent_tools
from agent_tools import get_scenario_summary, evaluate_plan, build_plan

MODEL = "qwen2.5:7b"
MAX_ROUNDS = 15
TOOLS = {"get_scenario_summary": get_scenario_summary,
         "build_plan": build_plan,
         "evaluate_plan": evaluate_plan}

SYSTEM_PROMPT = """You are a planning agent for a user terminal that can connect to LEO satellites or to a HAPS.
HAPS use is limited by a budget of minutes. Your job is to turn the operator's goal into a HAPS plan.
Steps:
1. Call get_scenario_summary.
2. Decide the settings for build_plan from the operator's goal:
   - max_haps_minutes: the most HAPS minutes to use. Use the full budget unless the goal says
     to use fewer or to keep some in reserve.
   - min_gain_mbps: 0, unless the goal says HAPS should only be used when it adds at least
     a certain throughput.
   - minimise_haps_use: true only if the goal asks to use HAPS as little as possible, or only
     as an emergency backup. Otherwise false. Outage minutes are always covered first by
     build_plan, so a goal that mentions avoiding outages does not by itself need this setting.
3. Call build_plan with those settings.
4. Call evaluate_plan with the minute ranges returned by build_plan.
5. End with one line in exactly this format:
FINAL PLAN: <the minute ranges from build_plan>
Then explain in two or three sentences which settings you chose and why. Quote the settings
exactly as shown in the "Settings used" line, and use only numbers from the tool outputs."""


def run_agent(goal, budget, verbose=True):
    agent_tools.BUDGET = budget
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"HAPS budget: {budget} minutes.\nGoal: {goal}"},
    ]
    calls = []
    for round_number in range(MAX_ROUNDS):
        response = ollama.chat(model=MODEL, messages=messages,
                               tools=list(TOOLS.values()), options={"temperature": 0})
        msg = response.message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content, calls

        for call in msg.tool_calls:
            name = call.function.name
            args = call.function.arguments
            calls.append((name, args))
            if verbose:
                print(f"\n[Agent calls {name}({args})]")
            try:
                result = TOOLS[name](**args)
            except (KeyError, TypeError):
                result = f"Error: the tool {name} was called incorrectly."
            if verbose:
                print(result)
            messages.append({"role": "tool", "content": result, "tool_name": name})

    return "Agent did not finish within the round limit.", calls


def extract_plan(text):
    matches = re.findall(r"FINAL PLAN:\s*(.+)", text)
    if len(matches) != 1:
        return None
    return matches[0].strip()


if __name__ == "__main__":
    goal = "Avoid all outages first. Then make the average throughput as high as possible."
    budget = 15

    answer, calls = run_agent(goal, budget)
    print("\n=== Agent's final answer ===")
    print(answer)

    plan = extract_plan(answer)
    print("\n=== Independent check of the final plan ===")
    if plan is None:
        print("Invalid answer: there must be exactly one FINAL PLAN line.")
    else:
        print("Plan:", plan)
        print(evaluate_plan(plan))