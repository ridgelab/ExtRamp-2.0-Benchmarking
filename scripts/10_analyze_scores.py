# This script reads in the Homo sapiens score file and creates three plots:
# 1. A histogram of ramp strength scores
# 2. A histogram of ramp robustness scores
# 3. A scatter plot of ramp strength vs robustness scores

import matplotlib.pyplot as plt

in_path = "../outputs/scores/GCF_000001405.40-hmean-w9-2.0-scores.tsv"

header_to_scores = {}

with open(in_path, "r") as f:
    header = f.readline()
    for line in f:
        items = line.strip().split("\t")
        header = items[0]
        strength_score = float(items[5])
        robustness_score = float(items[10])
        header_to_scores[header] = (strength_score, robustness_score)

ramp_strengths = [score[0] for score in header_to_scores.values()]
ramp_robustnesses = [score[1] for score in header_to_scores.values()]

# Plot a ramp strength histogram
strength_histogram_path = "../outputs/scores/ramp_strength_frequency.png"
strength_histogram_path_tif = "../outputs/scores/ramp_strength_frequency.tif"
plt.figure(figsize=(5, 5))
plt.hist(ramp_strengths, bins=100, color='gray')
plt.title("Ramp Strength Frequency", fontsize=16)
plt.xlabel("Ramp Strength", fontsize=14)
plt.ylabel("Frequency", fontsize=14)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(strength_histogram_path, dpi=350)
plt.savefig(strength_histogram_path_tif, dpi=350)

# Plot a ramp robustness histogram
robustness_histogram_path = "../outputs/scores/ramp_robustness_frequency.png"
robustness_histogram_path_tif = "../outputs/scores/ramp_robustness_frequency.tif"
plt.figure(figsize=(5, 5))
plt.hist(ramp_robustnesses, bins=100, color='gray')
plt.title("Ramp Robustness Frequency", fontsize=16)
plt.xlabel("Ramp Robustness", fontsize=14)
plt.ylabel("Frequency", fontsize=14)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(robustness_histogram_path, dpi=350)
plt.savefig(robustness_histogram_path_tif, dpi=350)

# Plot a scatter plot of ramp strength vs robustness
scores_scatter_path = "../outputs/scores/ramp_strength_vs_robustness.png"
scores_scatter_path_tif = "../outputs/scores/ramp_strength_vs_robustness.tif"
plt.figure(figsize=(5, 5))
plt.scatter(ramp_strengths, ramp_robustnesses, color='gray')
plt.title("Ramp Strength vs Robustness", fontsize=16)
plt.xlabel("Ramp Strength", fontsize=14)
plt.ylabel("Ramp Robustness", fontsize=14)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig(scores_scatter_path, dpi=350)
plt.savefig(scores_scatter_path_tif, dpi=350)

# Plot all three in one figure
combined_path = "../outputs/scores/ramp_strength_robustness_combined.png"
combined_path_tif = "../outputs/scores/ramp_strength_robustness_combined.tif"
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
axs[0].hist(ramp_strengths, bins=100, color='gray')
axs[0].set_title("Ramp Strength Frequency", fontsize=16)
axs[0].set_xlabel("Ramp Strength", fontsize=14)
axs[0].set_ylabel("Frequency", fontsize=14)
axs[0].grid(alpha=0.2)
axs[1].hist(ramp_robustnesses, bins=100, color='gray')
axs[1].set_title("Ramp Robustness Frequency", fontsize=16)
axs[1].set_xlabel("Ramp Robustness", fontsize=14)
axs[1].set_ylabel("Frequency", fontsize=14)
axs[1].grid(alpha=0.2)
axs[2].scatter(ramp_strengths, ramp_robustnesses, color='gray')
axs[2].set_title("Ramp Strength vs Robustness", fontsize=16)
axs[2].set_xlabel("Ramp Strength", fontsize=14)
axs[2].set_ylabel("Ramp Robustness", fontsize=14)
axs[2].grid(alpha=0.2)
plt.tight_layout()
plt.savefig(combined_path, dpi=350)
plt.savefig(combined_path_tif, dpi=350)
plt.close()

print("Plots saved to ../outputs/scores/")