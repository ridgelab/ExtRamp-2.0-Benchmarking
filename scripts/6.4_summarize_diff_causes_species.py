# This script gets the number and percent of sequences that differ between version 1.0 and version 2.0 and the number and percent
# of these sequences that are the result of:
# 1. a bug fix that now includes the last window mean in calculations
# 2. differences in rounding passed the 14th decimal place

import sys
import os

def get_total_sequences(in_path, species_id):
    with open(in_path, "r") as inf:
        header = inf.readline()
        for line in inf:
            items = line.strip().split("\t")
            if items[0] == species_id:
                return int(items[2])
    return "NA"

def get_species_path(output_folder, version, mean, taxonomic_group, species_id):
    # get the path to the species folder
    taxonomic_folder = os.path.join(output_folder, version, mean, taxonomic_group)
    for file in os.listdir(taxonomic_folder):
        if species_id in file and file.endswith("-ramps.fa"):
            return os.path.join(taxonomic_folder, file)
    return None

def read_ramps_file(path):
    ramps = {}
    with open(path, "r") as inf:
        header = inf.readline().strip()
        seq = inf.readline().strip()
        while header:
            ramps[header] = seq
            header = inf.readline().strip()
            seq = inf.readline().strip()
    return ramps

def get_ramp_diffs(ramps1, ramps2):
    # get the headers not in both dictionaries
    diff_headers = set(ramps1.keys()).symmetric_difference(set(ramps2.keys()))
    # add headers that are in both dictionaries but with different ramp sequences
    for header in ramps1:
        if header in ramps2:
            if ramps1[header] != ramps2[header]:
                diff_headers.add(header)
    return diff_headers

if __name__ == "__main__":
    taxonomic_group = sys.argv[1] if len(sys.argv) > 1 else ""
    species_id = sys.argv[2] if len(sys.argv) > 2 else ""
    MEAN = sys.argv[3] if len(sys.argv) > 3 else "hmean"

    if not species_id or not taxonomic_group:
        print("Please provide a species ID and taxonomic group as the first two arguments.")
        sys.exit(1)

    BASE_OUTPUT_FOLDER="../outputs"
    benchmark1_summary_path = f"{BASE_OUTPUT_FOLDER}/benchmark1_summary_combined-{MEAN}.tsv"
    out_path = f"{BASE_OUTPUT_FOLDER}/benchmark1_difference_explanation-{species_id}-{taxonomic_group}-{MEAN}.tsv"

    # get the total valid sequences from the slurm file of version 2.0
    total_sequences = get_total_sequences(benchmark1_summary_path, species_id)

    total_diff_1_2 = 0
    total_diff_1_1_fixed = 0
    total_diff_1_2_rounding = 0
    total_diff_1_2_not_explained = 0

    # get the file paths that contain the species ID
    ramp1_path = get_species_path(BASE_OUTPUT_FOLDER, "1.0", MEAN, taxonomic_group, species_id)
    ramp1_fixed_path = get_species_path(BASE_OUTPUT_FOLDER, "1.0-fixed", MEAN, taxonomic_group, species_id)
    ramp2_path = get_species_path(BASE_OUTPUT_FOLDER, "2.0", MEAN, taxonomic_group, species_id)
            
    ramp1_fixed_truncated_path = get_species_path(BASE_OUTPUT_FOLDER, "1.0-fixed-truncated", MEAN, taxonomic_group, species_id)
    ramp2_truncated_path = get_species_path(BASE_OUTPUT_FOLDER, "2.0-truncated", MEAN, taxonomic_group, species_id)
    if os.path.exists(ramp1_path) and os.path.exists(ramp2_path) and os.path.exists(ramp1_fixed_path):
        # get the sequences from the 3 ramp files
        ramps1 = read_ramps_file(ramp1_path)
        ramps1_fixed = read_ramps_file(ramp1_fixed_path)
        ramps2 = read_ramps_file(ramp2_path)

        # get the headers that differ between 1.0 and 2.0 (either not shared or that have different sequences)
        diff_headers_total = get_ramp_diffs(ramps1, ramps2)
        diff_1_2 = len(diff_headers_total)
        total_diff_1_2 += diff_1_2

        if diff_1_2 > 0:
            # get the headers that differ between 1.0 and 1.0-fixed (either not shared or that have different sequences)
            diff_headers1_fixed = get_ramp_diffs(ramps1, ramps1_fixed)
            # only keep the headers that are also in diff_headers_total (an extra window mean somtimes puts the min in the first 8% of the gene)
            diff_headers1_fixed = diff_headers1_fixed.intersection(diff_headers_total)
            diff_1_1_fixed = len(diff_headers1_fixed)
            total_diff_1_1_fixed += diff_1_1_fixed

            # get the headers that differ between 1.0 and 2.0 not explained by 1.0-fixed
            diff_headers_other = diff_headers_total - diff_headers1_fixed

            if len(diff_headers_other) > 0:
                # if the contents of ramp1_fixed_truncated_path and ramp2_truncated_path are the same, all diff_headers_other are explained by rounding differences
                if os.path.exists(ramp1_fixed_truncated_path) and os.path.exists(ramp2_truncated_path):
                    ramp1_fixed_truncated = read_ramps_file(ramp1_fixed_truncated_path)
                    ramp2_truncated = read_ramps_file(ramp2_truncated_path)
                    if ramp1_fixed_truncated == ramp2_truncated:
                        total_diff_1_2_rounding += len(diff_headers_other)
                    else:
                        # get the headers and sequences that differ between the truncated files
                        diff_headers_truncated = get_ramp_diffs(ramp1_fixed_truncated, ramp2_truncated)
                        # remove any headers from diff_headers_truncated that are not in diff_headers_other (these were altered due to the truncation, not alterations found between v1.0 and v2.0)
                        diff_headers_truncated = diff_headers_truncated.intersection(diff_headers_other)
                        # count the headers in diff_headers_other that are not in diff_headers_truncated as explained by rounding differences
                        diff_headers_other_rounding = diff_headers_other - diff_headers_truncated
                        total_diff_1_2_rounding += len(diff_headers_other_rounding)

                        # the rest of the headers are unexplained
                        if len(diff_headers_truncated) > 0:
                            for header in diff_headers_truncated:
                                print(f"Unexplained difference for {header} in {species_id} | {taxonomic_group} | {ramp1_fixed_truncated_path} | {ramp2_truncated_path}")
                                total_diff_1_2_not_explained += 1
                else:
                    # if this error is printed, the results will not be accurat- fix the issue and rerun
                    print(f"Truncated files missing for {species_id} | {taxonomic_group}")
                    total_diff_1_2_not_explained += len(diff_headers_other)
    else:
        if not os.path.exists(ramp1_path):
            print(f"\tMissing: {ramp1_path}")
        if not os.path.exists(ramp1_fixed_path):
            print(f"\tMissing: {ramp1_fixed_path}")
        if not os.path.exists(ramp2_path):
            print(f"\tMissing: {ramp2_path}")
    # write the results to a TSV file
    percent_diff = (total_diff_1_2 / total_sequences) * 100 if total_sequences > 0 else 0
    percent_last_window = (total_diff_1_1_fixed / total_sequences) * 100 if total_sequences > 0 else 0
    percent_diff_rounding = (total_diff_1_2_rounding / total_sequences) * 100 if total_sequences > 0 else 0
    percent_diff_other = (total_diff_1_2_not_explained / total_sequences) * 100 if total_sequences > 0 else 0
    with open(out_path, "w") as outf:
        outf.write("total sequences\ttotal differing\tlast window\trounding\tother\tpercent differing\tpercent last window\tpercent rounding\tpercent other\n")
        outf.write(f"{total_sequences}\t{total_diff_1_2}\t{total_diff_1_1_fixed}\t{total_diff_1_2_rounding}\t{total_diff_1_2_not_explained}\t{percent_diff}\t{percent_last_window}\t{percent_diff_rounding}\t{percent_diff_other}\n")
    print("done.")