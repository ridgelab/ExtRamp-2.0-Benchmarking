# This script creates two hypothetical plots side by side to illustrate how ramp strength and 
# robustness scores are calculated.

import matplotlib.pyplot as plt

def createPlotsSideBySide(yPoints1, yPoints2, plotPath):
    xPoints1 = list(range(1, len(yPoints1) + 1))
    xPoints2 = list(range(1, len(yPoints2) + 1))

    # note: ramp cutoff is normally 8% of the total length of the list by default, 
    # but here we set it manually for demonstration purposes
    ramp_cutoff1 = 3
    ramp_cutoff2 = 3

    # get the minimum in ramp and non-ramp regions
    min_ramp_region1 = min(yPoints1[:ramp_cutoff1+1])
    min_non_ramp_region1 = min(yPoints1[ramp_cutoff1+1:])
    min_ramp_region2 = min(yPoints2[:ramp_cutoff2+1])
    min_non_ramp_region2 = min(yPoints2[ramp_cutoff2+1:])

    # create figure with two subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # plot the first figure (ramp present)
    axes[0].plot(xPoints1, yPoints1, marker='o', linestyle='-', color='orange', linewidth=2)
    axes[0].axhline(y=min_ramp_region1, color='gray', linestyle='--')
    axes[0].axhline(y=min_non_ramp_region1, color='gray', linestyle='--')
    axes[0].axvline(x=ramp_cutoff1, color='gray', linestyle='--')
    axes[0].set_ylim(0, 1)
    axes[0].set_xlabel("9-Codon Sliding Window")
    axes[0].set_ylabel("Mean Efficiency")
    axes[0].set_title("Wild-type Ramp")
    # plot the ramp strength score as text between the two horizontal lines
    ramp_strength_score1 = min_non_ramp_region1 - min_ramp_region1
    axes[0].text(0.775, 0.425, f"Strength: {ramp_strength_score1:.2f}", transform=axes[0].transAxes, 
                 fontsize=10, verticalalignment='bottom', horizontalalignment='center')
    # draw error bars between the two horizontal lines
    axes[0].errorbar(7.5, (min_ramp_region1 + min_non_ramp_region1) / 2, 
                     yerr=[(ramp_strength_score1 - 0.02) / 2], color='black', capsize=5)

    # plot the second figure (ramp absent)
    axes[1].plot(xPoints2, yPoints2, marker='o', linestyle='-', color='orange', linewidth=2)
    axes[1].axhline(y=min_ramp_region2, color='gray', linestyle='--')
    axes[1].axhline(y=min_non_ramp_region2, color='gray', linestyle='--')
    axes[1].axvline(x=ramp_cutoff2, color='gray', linestyle='--')
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("9-Codon Sliding Window")
    axes[1].set_title("Wild-type Ramp Absence")
    # plot the ramp strength score as text between the two horizontal lines
    ramp_strength_score2 = min_non_ramp_region2 - min_ramp_region2
    axes[1].text(0.475, 0.375, f"Strength: {ramp_strength_score2:.2f}", transform=axes[1].transAxes, 
                 fontsize=10, verticalalignment='bottom', horizontalalignment='center')
    # draw error bars between the two horizontal lines
    axes[1].errorbar(4, (min_ramp_region2 + min_non_ramp_region2) / 2, 
                    yerr=[(ramp_strength_score2*-1 - 0.02) / 2], color='black', capsize=5)

    plt.tight_layout()
    plt.savefig(plotPath, dpi=300)

    print(f"Plots saved as {plotPath}")

yPoints1 = [0.4, 0.45, 0.6, 0.55, 0.65, 0.5, 0.7, 0.65, 0.75, 0.7, 0.8]
yPoints2 = [0.65, 0.56, 0.62, 0.82, 0.48, 0.58, 0.45, 0.42, 0.62, 0.35, 0.67]

createPlotsSideBySide(yPoints1, yPoints2, "hypothetical_plots.png")
