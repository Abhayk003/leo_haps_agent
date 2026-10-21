from goal_checker import extract_reserve

TESTS = [
    ("Avoid all outages first. Then make the average throughput as high as possible.", 0),
    ("Avoid all outages first. Then make the average throughput as high as possible. "
     "The rain forecast may be wrong, so keep some HAPS minutes ready for surprises.", 3),
    ("Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput.", 0),
    ("Use HAPS as little as possible, but never allow an outage. The weather forecast is unreliable.", 3),
    ("Maximise throughput, and hold back 5 HAPS minutes in case the forecast is wrong.", 5),
    ("Use at most 10 HAPS minutes, and keep 2 of them ready for unexpected outages.", 2),
    ("Use HAPS as little as possible, but never allow an outage.", 0),
    ("Only use HAPS when it adds at least 100 Mbps.", 0),
    ("HAPS should be an emergency backup only.", 0),
    ("Get the highest possible average throughput.", 0),
    ("Use at most 10 HAPS minutes, and only where HAPS adds at least 150 Mbps.", 0),
    ("Plan for the possibility that the rain arrives later than forecast.", 3),
    ("Hold 4 HAPS minutes back for surprises.", 4),
]

correct = 0
for goal, expected in TESTS:
    got = extract_reserve(goal)
    ok = got == expected
    correct += ok
    print(f"{'CORRECT' if ok else 'WRONG  '}  expected {expected}, got {got}  | {goal}")
print()
print(f"{correct} of {len(TESTS)} correct")