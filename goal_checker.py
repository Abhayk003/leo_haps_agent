import json
import ollama

MODEL = "qwen2.5:7b"

CHECK_PROMPT = """You check operator goals for a HAPS planning tool.
The tool can control only these things:
(a) the number of HAPS minutes used, up to a budget,
(b) a minimum throughput gain required for each HAPS minute,
(c) whether HAPS is used only to avoid outages, as little as possible,
(d) keeping some HAPS minutes unplanned, ready for unexpected outages or forecast errors.
Avoiding outages, maximising throughput, keeping HAPS minutes in reserve, preparing for
forecast errors and using fewer minutes than the budget are always supported.

List only the parts of the goal that ask for something the tool cannot control:
- "handovers": a limit or preference about the number of handovers
- "delay": a limit or preference about delay or latency
- "time_window": a rule about when, or in which minutes, HAPS is used
- "other": any other request unrelated to (a), (b), (c) and (d)
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


RESERVE_PROMPT = """You read an operator goal for a HAPS planning system. Decide how many HAPS
minutes should be kept unplanned, ready for outages that the weather forecast did not predict.
- If the goal says the forecast or weather may be wrong or unreliable, or asks to keep minutes
  ready for unexpected outages or surprises: use the number of minutes the goal gives,
  or 3 if it gives none.
- Otherwise use 0.
- Minutes kept "in reserve for other users" are about sharing HAPS with others, not about
  forecast errors. They do not count here; use 0 for them."""

RESERVE_SCHEMA = {
    "type": "object",
    "properties": {"reserve_minutes": {"type": "integer", "minimum": 0}},
    "required": ["reserve_minutes"],
}

def extract_reserve(goal):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": RESERVE_PROMPT},
                  {"role": "user", "content": f"Goal: {goal}"}],
        format=RESERVE_SCHEMA,
        options={"temperature": 0},
    )
    try:
        return max(0, int(json.loads(response.message.content)["reserve_minutes"]))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return 0

    

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