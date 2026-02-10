# This script plots the time and memory to number of sequences comparisons between ExtRamp v1.0 and v2.0 for
# all four valid means supported by ExtRamp (harmonic mean, geometric mean, arithmetic mean, median).
# It generates two plots for each mean type: one for time and one for memory. 

import sys
import os
import matplotlib.pyplot as plt
import statistics
import numpy as np

def plot_data(species_id_to_data, out_path, out_path_tif, type, mean_label):
    # Prepare data for plotting
    num_seqs = [data["num_seqs"] for data in species_id_to_data.values()]
    if type == "Time":
        means1 = [data["mean_time1"] for data in species_id_to_data.values()]
        sds1 = [data["sd_time1"] for data in species_id_to_data.values()]
        means2 = [data["mean_time2"] for data in species_id_to_data.values()]
        sds2 = [data["sd_time2"] for data in species_id_to_data.values()]
    elif type == "Memory":
        means1 = [data["mean_mem1"] for data in species_id_to_data.values()]
        sds1 = [data["sd_mem1"] for data in species_id_to_data.values()]
        means2 = [data["mean_mem2"] for data in species_id_to_data.values()]
        sds2 = [data["sd_mem2"] for data in species_id_to_data.values()]

    plt.figure(figsize=(4, 4))
    plt.errorbar(num_seqs, means1, yerr=sds1, fmt="o", label="ExtRamp 1.0", color="#E69F00", ecolor="#E69F00", capsize=5)
    plt.errorbar(num_seqs, means2, yerr=sds2, fmt="o", label="ExtRamp 2.0", color="#56B4E9", ecolor="#56B4E9", capsize=5)
    # Plot a best fit line for each version
    z1 = np.polyfit(num_seqs, means1, 1)
    p1 = np.poly1d(z1)
    plt.plot(sorted(num_seqs), p1(sorted(num_seqs)), "--", color="#E69F00")
    z2 = np.polyfit(num_seqs, means2, 1)
    p2 = np.poly1d(z2)
    plt.plot(sorted(num_seqs), p2(sorted(num_seqs)), "--", color="#56B4E9")
    plt.xscale("log")
    plt.xlabel("Number of Sequences (Log Scale)", fontsize=14)
    if type == "Memory":
        plt.ylabel("Memory (GB)", fontsize=14)
    elif type == "Time":
        plt.ylabel("Time (Minutes)", fontsize=14)
    plt.title(f"{mean_label}", fontsize=16)
    plt.legend()
    plt.grid(True, which="both", ls="--", linewidth=0.1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=350)
    plt.savefig(out_path_tif, dpi=350)
    plt.close()
    print(f"Plot saved to {out_path} and {out_path_tif}")

def plot_data2(species_id_to_data, out_path, out_path_tif, mean_label):
    # plot the time and memory data in two connected plots
    # Prepare data for plotting
    num_seqs = [data["num_seqs"] for data in species_id_to_data.values()]
    mean_time1 = [data["mean_time1"] for data in species_id_to_data.values()]
    sd_time1 = [data["sd_time1"] for data in species_id_to_data.values()]
    mean_time2 = [data["mean_time2"] for data in species_id_to_data.values()]
    sd_time2 = [data["sd_time2"] for data in species_id_to_data.values()]
    mean_mem1 = [data["mean_mem1"] for data in species_id_to_data.values()]
    sd_mem1 = [data["sd_mem1"] for data in species_id_to_data.values()]
    mean_mem2 = [data["mean_mem2"] for data in species_id_to_data.values()]
    sd_mem2 = [data["sd_mem2"] for data in species_id_to_data.values()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4, 8))

    ax1.errorbar(num_seqs, mean_time1, yerr=sd_time1, fmt="o", label="ExtRamp 1.0", color="#E69F00", ecolor="#E69F00", capsize=5)
    ax1.errorbar(num_seqs, mean_time2, yerr=sd_time2, fmt="o", label="ExtRamp 2.0", color="#56B4E9", ecolor="#56B4E9", capsize=5)
    z1 = np.polyfit(num_seqs, mean_time1, 1)
    p1 = np.poly1d(z1)
    ax1.plot(sorted(num_seqs), p1(sorted(num_seqs)), "--", color="#E69F00")
    z2 = np.polyfit(num_seqs, mean_time2, 1)
    p2 = np.poly1d(z2)
    ax1.plot(sorted(num_seqs), p2(sorted(num_seqs)), "--", color="#56B4E9")
    ax1.set_ylim(top=max(max(mean_time1), max(mean_time2)) * 1.1)
    ax1.set_xscale("log")
    ax1.set_ylabel("Time (Minutes)", fontsize=14)
    ax1.set_title(f"{mean_label}", fontsize=16)
    ax1.legend()
    ax1.grid(True, which="both", ls="--", linewidth=0.1)

    ax2.errorbar(num_seqs, mean_mem1, yerr=sd_mem1, fmt="o", label="ExtRamp 1.0", color="#E69F00", ecolor="#E69F00", capsize=5)
    ax2.errorbar(num_seqs, mean_mem2, yerr=sd_mem2, fmt="o", label="ExtRamp 2.0", color="#56B4E9", ecolor="#56B4E9", capsize=5)
    z1 = np.polyfit(num_seqs, mean_mem1, 1)
    p1 = np.poly1d(z1)
    ax2.plot(sorted(num_seqs), p1(sorted(num_seqs)), "--", color="#E69F00")
    z2 = np.polyfit(num_seqs, mean_mem2, 1)
    p2 = np.poly1d(z2)
    ax2.plot(sorted(num_seqs), p2(sorted(num_seqs)), "--", color="#56B4E9")
    ax2.set_ylim(top=max(max(mean_mem1), max(mean_mem2)) * 1.1)
    ax2.set_xscale("log")
    ax2.set_xlabel("Number of Sequences (Log Scale)", fontsize=14)
    ax2.set_ylabel("Memory (GB)", fontsize=14)
    ax2.grid(True, which="both", ls="--", linewidth=0.1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=350)
    plt.savefig(out_path_tif, dpi=350)
    plt.close()
    print(f"Plot saved to {out_path} and {out_path_tif}")

def write_summary_stats(species_id_to_data, out_path):
    with open(out_path, "w") as outf:
        outf.write("taxonomic_group\tspecies_id\tnum_sequences\tmean_time1\tsd_time1\tmean_mem1\tsd_mem1\tmean_time2\tsd_time2\tmean_mem2\tsd_mem2\ttimes_faster\ttimes_mem_efficient\n")
        # sort by taxonomic group, then num sequences
        sorted_items = sorted(species_id_to_data.items(), key=lambda x: (x[1]["tax_group"], x[1]["num_seqs"]))
        for species_id, data in sorted_items:
            times_faster = data["mean_time1"] / data["mean_time2"]
            times_mem_efficient = data["mean_mem1"] / data["mean_mem2"]
            outf.write(f"{data["tax_group"]}\t{species_id}\t{data["num_seqs"]}\t{data["mean_time1"]}\t{data["sd_time1"]}\t{data["mean_mem1"]}\t{data["sd_mem1"]}\t{data["mean_time2"]}\t{data["sd_time2"]}\t{data["mean_mem2"]}\t{data["sd_mem2"]}\t{times_faster}\t{times_mem_efficient}\n")
        print(f"Summary stats written to {out_path}")

def prep_data(in_path):
    species_id_to_data = {}
    with open(in_path, "r") as inf:
        header = inf.readline()
        for line in inf:
            items = line.strip().split("\t")
            version = items[0]
            tax_group = items[1]
            species_id = items[2]
            num_seqs = int(items[4])
            time = float(items[5]) / 60 # convert to minutes
            mem = float(items[6]) / 1000000  # convert to GB
            if species_id not in species_id_to_data:
                species_id_to_data[species_id] = {"tax_group": tax_group, "num_seqs": num_seqs, "time1": [], "mem1": [], "time2": [], "mem2": []}
            if version == "1.0":
                species_id_to_data[species_id]["time1"].append(time)
                species_id_to_data[species_id]["mem1"].append(mem)
            elif version == "2.0":
                species_id_to_data[species_id]["time2"].append(time)
                species_id_to_data[species_id]["mem2"].append(mem)

    for species_id, data in species_id_to_data.items():
        data["mean_time1"] = sum(data["time1"]) / len(data["time1"])
        data["sd_time1"] = statistics.stdev(data["time1"]) if len(data["time1"]) > 1 else "NA"
        data["mean_mem1"] = sum(data["mem1"]) / len(data["mem1"])
        data["sd_mem1"] = statistics.stdev(data["mem1"]) if len(data["mem1"]) > 1 else "NA"
        data["mean_time2"] = sum(data["time2"]) / len(data["time2"])
        data["sd_time2"] = statistics.stdev(data["time2"]) if len(data["time2"]) > 1 else "NA"
        data["mean_mem2"] = sum(data["mem2"]) / len(data["mem2"])
        data["sd_mem2"] = statistics.stdev(data["mem2"]) if len(data["mem2"]) > 1 else "NA"
    
    return species_id_to_data

if __name__ == "__main__":
    mean_labels = {"hmean": "Harmonic Mean", "gmean": "Geometric Mean", "mean": "Arithmetic Mean", "median": "Median"}
    BASE_OUT_DIR = "../outputs/time_mem"
    for mean, mean_label in mean_labels.items():
        in_path = f"{BASE_OUT_DIR}/benchmark2_results_{mean}.tsv"
        time_out_path = f"{BASE_OUT_DIR}/num_seq_to_time-{mean}.png"
        mem_out_path = f"{BASE_OUT_DIR}/num_seq_to_mem-{mean}.png"
        fig_path = f"{BASE_OUT_DIR}/num_seq_to_time_mem-{mean}.png"

        time_out_path_tif = f"{BASE_OUT_DIR}/num_seq_to_time-{mean}.tif"
        mem_out_path_tif = f"{BASE_OUT_DIR}/num_seq_to_mem-{mean}.tif"
        fig_path_tif = f"{BASE_OUT_DIR}/num_seq_to_time_mem-{mean}.tif"

        summary_out_path = f"{BASE_OUT_DIR}/benchmark2_summary_{mean}.tsv"
        if not os.path.exists(in_path):
            print(f"Input file {in_path} does not exist. Skipping {mean}.")
            continue
        print(f"Processing {mean}...")
        # Process the data
        species_id_to_data = prep_data(in_path)
        # Plot the data
        # Create the time plot
        plot_data(species_id_to_data, time_out_path, time_out_path_tif, "Time", mean_label)
        # Create the memory plot
        plot_data(species_id_to_data, mem_out_path, mem_out_path_tif, "Memory", mean_label)
        # Create the combined time and memory plot
        plot_data2(species_id_to_data, fig_path, fig_path_tif, mean_label)
        # Write summary stats
        write_summary_stats(species_id_to_data, summary_out_path)

    print("done.")