# This script plots three graphs:
# 1. a plot of all the ramp strength to ramp robustness scores for humans, with blue indicating sequences that did not change status or length between ExtRamp versions,
# and red/yellow indicating sequences that did change status/length either because of last window changes or rounding changes respectively.
# 2. a histogram of ramp strength score percents for sequences that changed status/length because of last window or rounding changes between ExtRamp versions compared to those that did not change.
# 3. a histogram of ramp robustness score percents for sequences that changed status/length because of last window or rounding changes between ExtRamp versions compared to those that did not change.
# The log file additionally contains:
# 1. the counts and percentages of sequences whose status or length changed because of last window or rounding changes between ExtRamp versions.
# 2. the means and standard deviations of the ramp strength and robustness scores for each group.
# Magnitude was used for robustness scores in mean, std, and t-test calculations since robustness scores are bimodal.

import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
from math import ceil, floor

def get_scores(scores_path):
    header_to_scores = {}
    with open(scores_path, "r") as inf:
        _ = inf.readline()
        for line in inf:
            line = line.strip()
            items = line.split("\t")
            header = items[0]
            ramp_strength = float(items[5])
            ramp_robustness = float(items[-1])
            header_to_scores[header] = (ramp_strength, ramp_robustness)
    return header_to_scores

def get_ramp_lengths(path):
    ramp_lengths = {}
    with open(path, "r") as inf:
        header = inf.readline().strip()
        seq = inf.readline().strip()
        while header:
            ramp_lengths[header] = len(seq)
            header = inf.readline().strip()
            seq = inf.readline().strip()
    return ramp_lengths

def get_all_changed_header_scores(v1_lengths, v2_lengths, header_to_scores):
    all_changed_headers = set(v1_lengths.keys()).symmetric_difference(set(v2_lengths.keys()))
    for header, v2_length in v2_lengths.items():
        if header in v1_lengths:
            v1_length = v1_lengths[header]
            if v2_length != v1_length:
                all_changed_headers.add(header)
    all_changed_headers_to_scores = {header: header_to_scores[header] for header in all_changed_headers}
    # remove last window changed headers from the main header_to_scores dictionary
    for header in all_changed_headers_to_scores:
        if header in header_to_scores:
            del header_to_scores[header]
    return all_changed_headers_to_scores, header_to_scores

def get_last_window_changed_header_scores(all_changed_headers_to_scores, v1_lengths, v2_lengths, v1_fixed_lengths, header_to_scores):
    last_window_changed_headers = set()
    for header in all_changed_headers_to_scores:
        v1_length = v1_lengths.get(header, None)
        v2_length = v2_lengths.get(header, None)
        v1_fixed_length = v1_fixed_lengths.get(header, None)
        # last window changed if the header is present in one version but not the other, but v1_fixed agrees with v2
        if v1_length != v2_length and v2_length == v1_fixed_length:
            last_window_changed_headers.add(header)
    last_window_changed_headers_to_scores = {header: all_changed_headers_to_scores[header] for header in last_window_changed_headers}
    # remove last window changed headers from all_changed_headers_to_scores
    # the remaining headers are rounding changed
    for header in last_window_changed_headers_to_scores:
        if header in all_changed_headers_to_scores:
            del all_changed_headers_to_scores[header]
    return last_window_changed_headers_to_scores, all_changed_headers_to_scores

def get_species_points(scores_path, v1_ramps_path, v2_ramps_path, v1_fixed_ramps_path):
    # get the ramp strength and robustness scores
    header_to_scores = get_scores(scores_path)

    # determine which sequences changed due to last window or rounding changes between ExtRamp versions
    v1_ramp_lengths = get_ramp_lengths(v1_ramps_path)
    v2_ramp_lengths = get_ramp_lengths(v2_ramps_path)
    v1_fixed_ramp_lengths = get_ramp_lengths(v1_fixed_ramps_path)

    all_changed_headers_to_scores, header_to_scores = get_all_changed_header_scores(v1_ramp_lengths, v2_ramp_lengths, header_to_scores)
    last_window_changed_headers_to_scores, rounding_changed_header_to_scores = get_last_window_changed_header_scores(all_changed_headers_to_scores, v1_ramp_lengths, v2_ramp_lengths, v1_fixed_ramp_lengths, header_to_scores)

    # get points for each category
    # unchanged sequences
    x_points_unchanged = []
    y_points_unchanged = []
    for header in header_to_scores:
        strength, robustness = header_to_scores[header]
        x_points_unchanged.append(strength)
        y_points_unchanged.append(robustness)
    # last window changed sequences
    x_points_last_window_changed = []
    y_points_last_window_changed = []
    for header in last_window_changed_headers_to_scores:
        strength, robustness = last_window_changed_headers_to_scores[header]
        x_points_last_window_changed.append(strength)
        y_points_last_window_changed.append(robustness)
    # rounding changed sequences
    x_points_rounding_changed = []
    y_points_rounding_changed = []
    for header in rounding_changed_header_to_scores:
        strength, robustness = rounding_changed_header_to_scores[header]
        x_points_rounding_changed.append(strength)
        y_points_rounding_changed.append(robustness)
    return x_points_unchanged, y_points_unchanged, x_points_last_window_changed, y_points_last_window_changed, x_points_rounding_changed, y_points_rounding_changed

def write_and_log(message, logf):
    print(message)
    logf.write(message + "\n")

if __name__ == "__main__":
    log_path = "../outputs/scores/plot_vulnerable_sequence_scores_mammalia.log"
    fig_path = "../outputs/scores/vulnerable_sequence_scores_mammalia.png"
    strength_hist_path = "../outputs/scores/vulnerable_sequence_strength_histogram_mammalia.png"
    robustness_hist_path = "../outputs/scores/vulnerable_sequence_robustness_histogram_mammalia.png"

    with open(log_path, "w") as logf:
        # get the paths for mammalian ramps and scores
        mammalian_2_path = "../outputs/2.0/hmean/mammalia/"
        mammalian_1_path = "../outputs/1.0/hmean/mammalia/"
        mammalian_1_fixed_path = "../outputs/1.0-fixed/hmean/mammalia/"
        species_to_paths = {}
        for file in os.listdir(mammalian_2_path):
            species_id = file.split("-")[0]
            if (species_id.startswith("GCF_") or species_id.startswith("GCA_")) and species_id not in species_to_paths:
                species_to_paths[species_id] = {}
            if file.endswith("scores.tsv"):
                species_to_paths[species_id]["scores"] = os.path.join(mammalian_2_path, file)
            elif file.endswith("ramps.fa"):
                species_to_paths[species_id]["ramps_2.0"] = os.path.join(mammalian_2_path, file)
        for file in os.listdir(mammalian_1_path):
            species_id = file.split("-")[0]
            if (species_id.startswith("GCF_") or species_id.startswith("GCA_")) and species_id not in species_to_paths:
                species_to_paths[species_id] = {}
            if file.endswith("ramps.fa"):
                species_to_paths[species_id]["ramps_1.0"] = os.path.join(mammalian_1_path, file)
        for file in os.listdir(mammalian_1_fixed_path):
            species_id = file.split("-")[0]
            if (species_id.startswith("GCF_") or species_id.startswith("GCA_")) and species_id not in species_to_paths:
                species_to_paths[species_id] = {}
            if file.endswith("ramps.fa"):
                species_to_paths[species_id]["ramps_1.0_fixed"] = os.path.join(mammalian_1_fixed_path, file)

        write_and_log(f"Found data for {len(species_to_paths)} mammalian species.", logf)

        total_x_points_unchanged = []
        total_y_points_unchanged = []
        total_x_points_last_window_changed = []
        total_y_points_last_window_changed = []
        total_x_points_rounding_changed = []
        total_y_points_rounding_changed = []
        species_processed = 0
        for species_id in species_to_paths:
            if "scores" in species_to_paths[species_id] and "ramps_1.0" in species_to_paths[species_id] and "ramps_2.0" in species_to_paths[species_id] and "ramps_1.0_fixed" in species_to_paths[species_id]:
                scores_path = species_to_paths[species_id]["scores"]
                v1_ramps_path = species_to_paths[species_id]["ramps_1.0"]
                v2_ramps_path = species_to_paths[species_id]["ramps_2.0"]
                v1_fixed_ramps_path = species_to_paths[species_id]["ramps_1.0_fixed"]
                x_points_unchanged, y_points_unchanged, x_points_last_window_changed, y_points_last_window_changed, x_points_rounding_changed, y_points_rounding_changed = get_species_points(scores_path, v1_ramps_path, v2_ramps_path, v1_fixed_ramps_path)
                total_x_points_unchanged.extend(x_points_unchanged)
                total_y_points_unchanged.extend(y_points_unchanged)
                total_x_points_last_window_changed.extend(x_points_last_window_changed)
                total_y_points_last_window_changed.extend(y_points_last_window_changed)
                total_x_points_rounding_changed.extend(x_points_rounding_changed)
                total_y_points_rounding_changed.extend(y_points_rounding_changed)
            else:
                write_and_log(f"Missing files for species {species_id}, skipping...", logf)
            species_processed += 1
            if species_processed % 10 == 0:
                write_and_log(f"Processed {species_processed} species...", logf)
        write_and_log(f"Processed {species_processed} species.", logf)
        write_and_log(f"", logf)

        total_x_points_changed = total_x_points_last_window_changed + total_x_points_rounding_changed
        total_y_points_changed = total_y_points_last_window_changed + total_y_points_rounding_changed

        unchanged_points = len(total_x_points_unchanged)
        last_window_changed_points = len(total_x_points_last_window_changed)
        rounding_changed_points = len(total_x_points_rounding_changed)
        total_changed_points = last_window_changed_points + rounding_changed_points
        total_points = (unchanged_points + total_changed_points)

        write_and_log(f"Unchanged points: {unchanged_points} ({unchanged_points/total_points:.2%})", logf)
        write_and_log(f"Last window changed points: {last_window_changed_points} ({last_window_changed_points/total_points:.2%})", logf)
        write_and_log(f"Rounding changed points: {rounding_changed_points} ({rounding_changed_points/total_points:.2%})", logf)
        write_and_log(f"Total changed points: {total_changed_points} ({total_changed_points/total_points:.2%})", logf)
        write_and_log(f"Total points: {total_points}", logf)
        write_and_log(f"", logf)

        plt.figure(figsize=(6,6))
        write_and_log("Plotting unchanged points...", logf)
        plt.scatter(total_x_points_unchanged, total_y_points_unchanged, color='blue', s=5, label='Unchanged')
        write_and_log("Plotting last window changed points...", logf)
        plt.scatter(total_x_points_last_window_changed, total_y_points_last_window_changed, color='red', s=5, label='Last Window Changed')
        write_and_log("Plotting rounding changed points...", logf)
        plt.scatter(total_x_points_rounding_changed, total_y_points_rounding_changed, color='yellow', s=5, label='Rounding Changed')
        # x ticks with step size 1.0
        plt.xticks(np.arange(floor(min(total_x_points_unchanged + total_x_points_changed)), ceil(max(total_x_points_unchanged + total_x_points_changed))+1, 1.0))
        ticks = plt.gca().get_xticks()
        labels = [str(int(t)) if i % 2 == 1 else '' for i, t in enumerate(ticks)]
        plt.gca().set_xticklabels(labels)
        plt.xlabel("Ramp Strength Score")
        plt.ylabel("Ramp Robustness Score")
        plt.legend()
        plt.ylim(-1.05, 1.05)
        plt.grid(True, which='both', linestyle='--', linewidth=0.2, )
        plt.tight_layout()
        plt.savefig(fig_path, dpi=300)
        write_and_log(f"Plot saved as {fig_path}", logf)
        write_and_log(f"", logf)

        # plot histogram of ramp strength scores for changed sequences compared to unchanged sequences
        unchanged_points_strength_mean = np.mean(total_x_points_unchanged)
        unchanged_points_strength_std = np.std(total_x_points_unchanged)
        changed_points_strength_mean = np.mean(total_x_points_changed)
        changed_points_strength_std = np.std(total_x_points_changed)
        write_and_log(f"Unchanged points strength mean: {unchanged_points_strength_mean:.2f}, std: {unchanged_points_strength_std:.2f}", logf)
        write_and_log(f"Changed points strength mean: {changed_points_strength_mean:.2f}, std: {changed_points_strength_std:.2f}", logf)
        write_and_log(f"", logf)

        # determine p-value using t-test
        t_stat, p_value = stats.ttest_ind(total_x_points_unchanged, total_x_points_changed, equal_var=False)
        write_and_log(f"T-test statistic: {t_stat:.2f}, p-value: {p_value:.2e}", logf)
        write_and_log(f"", logf)

        plt.figure(figsize=(6,4))
        write_and_log("Plotting histogram of ramp strength scores for unchanged points...", logf)
        plt.hist(total_x_points_unchanged, weights=np.ones(len(total_x_points_unchanged)) / len(total_x_points_unchanged) * 100, bins=30, alpha=0.5, color='blue', label='Unchanged')
        write_and_log("Plotting histogram of ramp strength scores for changed points...", logf)
        plt.hist(total_x_points_changed, weights=np.ones(len(total_x_points_changed)) / len(total_x_points_changed) * 100, bins=30, alpha=0.5, color='red', label='Changed')
        plt.xlabel("Ramp Strength Score")
        plt.ylabel("Percentage of Sequences")
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.2)
        plt.tight_layout()
        plt.savefig(strength_hist_path, dpi=300)
        write_and_log(f"Histogram saved as {strength_hist_path}", logf)  
        write_and_log(f"", logf)

        # plot histogram of ramp robustness scores for changed sequences compared to unchanged sequences
        unchanged_points_robustness_mean = np.mean(np.abs(total_y_points_unchanged))
        unchanged_points_robustness_std = np.std(np.abs(total_y_points_unchanged))
        changed_points_robustness_mean = np.mean(np.abs(total_y_points_changed))
        changed_points_robustness_std = np.std(np.abs(total_y_points_changed))
        write_and_log(f"Unchanged points robustness magnitudes mean: {unchanged_points_robustness_mean:.2f}, std: {unchanged_points_robustness_std:.2f}", logf)
        write_and_log(f"Changed points robustness magnitudes mean: {changed_points_robustness_mean:.2f}, std: {changed_points_robustness_std:.2f}", logf)
        write_and_log(f"", logf)

        # determine p-value using t-test on absolute values
        t_stat, p_value = stats.ttest_ind(np.abs(total_y_points_unchanged), np.abs(total_y_points_changed), equal_var=False)
        write_and_log(f"T-test statistic: {t_stat:.2f}, p-value: {p_value:.2e}", logf)
        write_and_log(f"", logf)

        plt.figure(figsize=(6,4))
        write_and_log("Plotting histogram of robustness scores for unchanged points...", logf)
        plt.hist(total_y_points_unchanged, weights=np.ones(len(total_y_points_unchanged)) / len(total_y_points_unchanged) * 100, bins=30, alpha=0.5, color='blue', label='Unchanged')
        write_and_log("Plotting histogram of robustness scores for changed points...", logf)
        plt.hist(total_y_points_changed, weights=np.ones(len(total_y_points_changed)) / len(total_y_points_changed) * 100, bins=30, alpha=0.5, color='red', label='Changed')
        plt.xlabel("Ramp Robustness Score")
        plt.ylabel("Percentage of Sequences")
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.2)
        plt.tight_layout()
        plt.savefig(robustness_hist_path, dpi=300)
        write_and_log(f"Histogram saved as {robustness_hist_path}", logf)
        write_and_log(f"", logf)
        
        write_and_log("Finished plotting all figures.", logf)
