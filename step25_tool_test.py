import ollama
from simulator import load_options

MODEL = "qwen2.5:3b"
OPTIONS = load_options()

def get_options(minute: int) -> str:
    """
    Get all available links (LEO satellites and HAPS) at a given minute of the scenario,
    ranked from highest to lowest capacity.

    Args:
      minute: The minute of the scenario, from 0 to 180.

    Returns:
      The best link by capacity, followed by all links ranked by capacity.
    """
    minute = int(minute)
    ranked = sorted(OPTIONS[minute], key=lambda o: o["capacity_mbps"], reverse=True)
    best = ranked[0]
    lines = [f"Best link by capacity: {best['option']} ({best['capacity_mbps']:.1f} Mbps)",
             "All links ranked by capacity:"]
    for rank, o in enumerate(ranked, start=1):
        lines.append(f"Rank {rank}: {o['option']}, capacity {o['capacity_mbps']:.1f} Mbps, "
                     f"SNR {o['snr_db']:.1f} dB")
    return "\n".join(lines)


TOOLS = {"get_options": get_options}

messages = [
    {"role": "system", "content": "You are a network assistant. Always use the tools to get data. Never guess numbers."},
    {"role": "user", "content": "At minute 90, which link has the highest capacity? Give its name and capacity."},
]

for round_number in range(5):
    response = ollama.chat(model=MODEL, messages=messages,
                           tools=[get_options], options={"temperature": 0})
    msg = response.message
    messages.append(msg)

    if not msg.tool_calls:
        print("Final answer:", msg.content)
        break

    for call in msg.tool_calls:
        name = call.function.name
        args = call.function.arguments
        print(f"Model called tool: {name}({args})")
        result = TOOLS[name](**args)
        print("Tool returned:")
        print(result)
        messages.append({"role": "tool", "content": result, "tool_name": name})