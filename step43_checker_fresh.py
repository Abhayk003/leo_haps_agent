from goal_checker import check_goal

TESTS = [
    ("Never let the user lose connection; otherwise save HAPS for other users.", set()),
    ("Spend at most half of the HAPS budget, and make it count.", set()),
    ("Squeeze out every bit of speed you can.", set()),
    ("Use HAPS only for big wins of 300 Mbps or more.", set()),
    ("Maximise throughput. I don't care about delay.", set()),
    ("Make sure the video call never freezes, and keep HAPS use small.", set()),
    ("Switch links as rarely as possible.", {"handovers"}),
    ("Keep latency under 2 ms at all times.", {"delay"}),
    ("Don't use HAPS during the first hour.", {"time_window"}),
    ("Prefer Starlink satellites over OneWeb.", {"other"}),
    ("Keep handovers low and latency minimal.", {"handovers", "delay"}),
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
print(f"{correct} of {len(TESTS)} correct on fresh goals")