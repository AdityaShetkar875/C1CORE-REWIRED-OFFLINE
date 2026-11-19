"""Urgency rules. All thresholds live here so they are easy to explain.
This orders a doctor's queue. It never diagnoses."""

# Critical limits: team assumptions, not clinical advice.
# name -> (critical_below, critical_above); None means no limit on that side.
CRITICAL = {
    "Potassium": (3.0, 6.0),
    "Sodium": (125, 155),
    "Glucose (Fasting)": (50, 300),
    "Haemoglobin": (8, None),
    "Creatinine": (None, 3.0),
    "Platelets": (50, None),
    "Calcium": (7.0, None),
}

# Words in the patient's message that raise the level one step
KEYWORDS = ["chest pain", "breathless", "fainted"]

LEVELS = ["routine", "watch", "urgent"]  # lowest to highest


def is_critical(name, value):
    # True if the value crosses the critical limit for this test
    low, high = CRITICAL.get(name, (None, None))
    return (low is not None and value < low) or (high is not None and value > high)


def is_out_of_range(value, low, high):
    # Outside the printed range? Bounds are inclusive, so equal is fine.
    return (low is not None and value < low) or (high is not None and value > high)


def test_level(t):
    # Level of one test: urgent, watch or routine
    if is_critical(t["name"], t["value"]):
        return "urgent"
    if is_out_of_range(t["value"], t["range_low"], t["range_high"]):
        return "watch"
    return "routine"


def raise_one_step(level):
    # routine -> watch -> urgent (urgent stays urgent)
    return LEVELS[min(LEVELS.index(level) + 1, 2)]


def rising_tests(history):
    """Names of tests rising over 3+ latest readings, all out of range.
    history: list of dicts with date, name, value, range_low, range_high."""
    names = {h["name"] for h in history}
    rising = []
    for name in sorted(names):
        series = sorted((h for h in history if h["name"] == name),
                        key=lambda h: h["date"])
        run = 1  # length of the latest rising, out-of-range streak
        for prev, cur in zip(series[-2::-1], series[::-1]):
            ok = (cur["value"] > prev["value"]
                  and is_out_of_range(prev["value"], prev["range_low"], prev["range_high"]))
            if not ok:
                break
            run += 1
        last = series[-1]
        if run >= 3 and is_out_of_range(last["value"], last["range_low"], last["range_high"]):
            rising.append(name)
    return rising


def assess(values, caption="", history=None):
    """values: list of dicts (name, value, range_low, range_high).
    Returns {level, worst, flags}."""
    level, worst = "routine", None
    for t in values:
        lvl = test_level(t)
        if LEVELS.index(lvl) > LEVELS.index(level):  # keep the worst test
            level, worst = lvl, t
    flags = []
    if history and rising_tests(history):
        flags.append("rising")
        if level == "routine":
            level = "watch"
    if any(k in caption.lower() for k in KEYWORDS):
        flags.append("keyword")
        level = raise_one_step(level)
    if worst:
        worst = {k: worst[k] for k in ("name", "value", "range_low", "range_high")}
    return {"level": level, "worst": worst, "flags": flags}
