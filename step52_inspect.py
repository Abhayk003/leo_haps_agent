import agent_tools
from agent import run_agent
from pipeline import FORECAST_NOTE

agent_tools.set_planning_data("scenario_links_forecast.csv", FORECAST_NOTE)
agent_tools.set_reserve(0)

goal = "Avoid all outages first. Then make the average throughput as high as possible."
answer, calls = run_agent(goal, 15, verbose=True)

print("\n=== Agent's final answer ===")
print(answer)