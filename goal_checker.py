import json
import ollama

MODEL = "qwen2.5:7b"

CHECK_PROMPT = """You check operator goals for a HAPS planning tool.
The tool can control only these things:
(a) the number of HAPS minutes used, up to a budget,
(b) a minimum throughput gain required for each HAPS minute,
(c) whether HAPS is used only to avoid outages, as little as possible.
Avoiding outages, maximising throughput, keeping HAPS minutes in reserve and using fewer
minutes than the budget are always supported.

List only the parts of the goal that ask for something the tool cannot control:
- "handovers": a limit or preference about the number of handovers
- "delay": a limit or preference about delay or latency
- "time_window": a rule about when, or in which minutes, HAPS is used
- "other": any other request unrelated to (a), (b) and (c)
Do not list a topic that the goal does not mention.
If every part of the goal is supported, return an empty list."""

SCHEMA = {
    "type": "object",
    "properties": {
        "unsupported": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string",
                                 "enum": ["handovers", "delay", "time_window", "other"]},
                    "reason": {"type": "string"},
                },
                "required": ["category", "reason"],
            },
        }
    },
    "required": ["unsupported"],
}


def check_goal(goal):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": CHECK_PROMPT},
                  {"role": "user", "content": f"Goal: {goal}"}],
        format=SCHEMA,
        options={"temperature": 0},
    )
    try:
        data = json.loads(response.message.content)
        return data["unsupported"]
    except (json.JSONDecodeError, KeyError):
        return [{"category": "other", "reason": "checker output could not be read"}]


if __name__ == "__main__":
    TESTS = [
        ("Avoid all outages first. Then make the average throughput as high as possible.", set()),
        ("Use HAPS as little as possible, but never allow an outage.", set()),
        ("Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput.", set()),
        ("Only use HAPS when it adds at least 100 Mbps.", set()),
        ("HAPS should be an emergency backup only.", set()),
        ("Get the highest possible average throughput.", set()),
        ("Use at most 10 HAPS minutes, and only where HAPS adds at least 150 Mbps.", set()),
        ("Keep the number of handovers below 30.", {"handovers"}),
        ("Always choose the link with the lowest delay.", {"delay"}),
        ("Use HAPS only between minute 100 and minute 130.", {"time_window"}),
        ("Make sure there are no outages and use exactly 20 HAPS minutes.", set()),
    ]

    correct = 0
    for goal, expected in TESTS:
        found = check_goal(goal)
        cats = {item["category"] for item in found}
        ok = cats == expected
        correct += ok
        print(f"{'CORRECT' if ok else 'WRONG  '}  expected {sorted(expected)}, got {sorted(cats)}  | {goal}")
        for item in found:
            print(f"           -> {item['category']}: {item['reason']}")
    print()
    print(f"{correct} of {len(TESTS)} correct")