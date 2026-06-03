from concurrent.futures import ThreadPoolExecutor
from pyXoXapi import get_rib, get_vantage_points
from datetime import datetime, timedelta
from collections import defaultdict

import matplotlib as mpl
mpl.use('PDF')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import ScalarFormatter


mpl.rcParams['pdf.use14corefonts']=True

mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
mpl.rcParams['xtick.major.pad'] = 10
mpl.rcParams['ytick.major.pad'] = 10
mpl.rcParams['xtick.minor.pad'] = 10
mpl.rcParams['ytick.minor.pad'] = 10


# Get the list of vantage points
selected_vantage_points = get_vantage_points(vantage_points=None)
print (selected_vantage_points)
# Define the reference date (July 31, 2024) and range of time intervals (1 to 30 days)
reference_date = "07/01/2024-00:00:00"
time_intervals = list(range(3, 31, 3))
print (time_intervals)

# Get the reference RIB for all vantage points (done once) and filter VPs with at least 100,000 prefixes
def get_reference_ribs_and_filter():
    ribs = {}
    i = 0
    for vantage_point in selected_vantage_points:
        print ('Get reference RIB for VP: {}'.format(vantage_point))
        rib = get_rib(vantage_point, date=reference_date)
        if len(rib) >= 100000:  # Only keep VPs with at least 100,000 prefixes
            ribs[vantage_point] = rib
            i += 1

            if i == 5:
                break
    return ribs

# Parallelize the comparison across intervals and VPs
def compute_proportion_for_vp(vantage_point, interval, rib_reference):
    comparison_date = (datetime.strptime(reference_date, '%m/%d/%Y-%H:%M:%S') + timedelta(days=interval)).strftime('%m/%d/%Y-00:00:00')
    print (vantage_point, interval, comparison_date)
    rib_comparison = get_rib(vantage_point, date=comparison_date)
    
    identical_count = 0
    total_count = len(rib_reference)

    for prefix in rib_reference:

        if prefix in rib_comparison:
            if (rib_reference[prefix][0] == rib_comparison[prefix][0]) and (rib_reference[prefix][1] == rib_comparison[prefix][1]):
                identical_count += 1


    # Return proportion as percentage
    if total_count > 0:
        return (identical_count / total_count) * 100
    return 0

def compute_proportions_for_interval(interval, rib_references):
    proportions = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(compute_proportion_for_vp, vp, interval, rib_references[vp])
            for vp in rib_references.keys()
        ]
        for future in futures:
            proportions.append(future.result())
    return proportions

# Get the reference RIBs for all VPs that meet the condition of having at least 100,000 prefixes
rib_references = get_reference_ribs_and_filter()

# Dictionary to store the proportions for each time interval across all VPs
proportions_per_interval = defaultdict(list)

# Iterate over each time interval (1 to 30 days) in parallel
with ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(compute_proportions_for_interval, interval, rib_references)
        for interval in time_intervals
    ]
    for future in futures:
        interval_proportions = future.result()
        proportions_per_interval[len(proportions_per_interval)] = interval_proportions

# Prepare data for plotting box plots
data_to_plot = [proportions_per_interval[i] for i in range(0, len(proportions_per_interval))]

# Colors for the "peach" color (peach is a soft, light orange-pink color)
peach_color = "#FFDAB9"

print (data_to_plot)

# Plotting the box plots with "peach" color and showing x-label only every 10 days
plt.figure(figsize=(10, 6))
boxplots = plt.boxplot(data_to_plot, positions=time_intervals, patch_artist=True, widths = 1.4, showfliers=False)

# Apply the "peach" color to all the boxes
for box in boxplots['boxes']:
    box.set(facecolor=peach_color)

plt.xlabel('Time difference (days)', fontsize=25, labelpad=10)
plt.ylabel('% of identical RIB entries', fontsize=25, labelpad=10)
plt.grid(True)

plt.ylim([0, 100])

# Customize x-ticks to show only every 10th day
plt.xticks(time_intervals)

plt.tight_layout()

# Save the figure as a PDF
plt.savefig("rib_identical_proportion_filtered_peach.pdf")

# Display the plot (optional, can be removed if not needed)
plt.show()

