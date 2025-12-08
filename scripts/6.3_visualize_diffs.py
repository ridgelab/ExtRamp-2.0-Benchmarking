# This script reads in the benchmark 1 difference explanation file and visualizes the differences
# between version 1 and 2 using two pie charts
# The first pie chart shows the percent of sequences that differ and
# the second shows the breakdown of the differing sequences

import matplotlib.pyplot as plt

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        val = f"{val:,}"
        return '{p:.2f}%\n({v})'.format(p=pct, v=val)
    return my_autopct

inpath = "../outputs/benchmark1_difference_explanation-final-hmean.tsv"
outpath = "../outputs/benchmark1_differences.png"

with open(inpath, "r") as inf:
    header = inf.readline().strip().split("\t")
    data = inf.readline().strip().split("\t")

total_sequences = int(data[0])
total_differing = int(data[1])
last_window = int(data[2])
rounding = int(data[3])
other = int(data[4])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.subplots_adjust(wspace=0.5)
fig.patch.set_facecolor('white')
colors = ['#888888', '#dddddd']
colors2 = ['#888888', '#bbbbbb']
labels = ['Differing', 'Same']
labels2 = ['Last Window Bug', 'Rounding']
sizes = [total_differing, total_sequences - total_differing]
sizes2 = [last_window, rounding]
if other > 0:
    colors2.append('#aaaaaa')
    labels2.append('Other')
    sizes2.append(other)
ax1.pie(sizes, labels=labels, colors=colors, autopct=make_autopct(sizes),
    shadow=False, startangle=140)
ax1.axis('equal')
ax1.set_title("Overall Differences")
ax2.pie(sizes2, labels=labels2, colors=colors2, autopct=make_autopct(sizes2),
    shadow=False, startangle=140)
ax2.axis('equal')
ax2.set_title("Difference Reasons")
plt.tight_layout()
# plt.show()
plt.savefig(outpath, dpi=350)
print(f"Figure saved to {outpath}")