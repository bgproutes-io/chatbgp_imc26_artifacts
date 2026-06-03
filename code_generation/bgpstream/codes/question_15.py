# Did the period from 7 March 2024 at 4:11:20 to 12 March 2024 at 9:14:13 experience a peak of withdrawals, which we define as twice the number of withdrawals compared to the average computed over ten other periods of equal duration?

import pybgpstream
from datetime import datetime, timedelta

# Target period
T_START = datetime(2024, 3, 7, 4, 11, 20)
T_END   = datetime(2024, 3, 12, 9, 14, 13)

PERIOD_LEN = int((T_END - T_START).total_seconds())

# Build list of 10 comparison periods of equal duration **before** target period
comparison_periods = []
cursor = T_START - timedelta(seconds=PERIOD_LEN)

for _ in range(10):
    p_end = cursor
    p_start = cursor - timedelta(seconds=PERIOD_LEN)
    comparison_periods.append((p_start, p_end))
    cursor = p_start

def count_withdrawals(t_from, t_until):
    """
    Count BGP withdrawals in the given interval.
    """
    stream = pybgpstream.BGPStream(
        from_time=t_from.strftime("%Y-%m-%d %H:%M:%S"),
        until_time=t_until.strftime("%Y-%m-%d %H:%M:%S"),
        record_type="updates"
    )

    w = 0

    for rec in stream.records():
        for elem in rec:
            if elem.type == "W":
                w += 1

    return w


# Count target-period withdrawals
target_withdrawals = count_withdrawals(T_START, T_END)

# Count comparison withdrawals
comparison_counts = []
for p_start, p_end in comparison_periods:
    c = count_withdrawals(p_start, p_end)
    comparison_counts.append(c)

avg_withdrawals = sum(comparison_counts) / len(comparison_counts)

# Check for peak:
# peak means: target_withdrawals >= 2 * average_of_10_periods
peak = target_withdrawals >= 2 * avg_withdrawals

print("Target period withdrawals:", target_withdrawals)
print("Average withdrawals over 10 comparison periods:", avg_withdrawals)
print("Peak condition (>= 2 × average):", peak)
