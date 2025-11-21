# This script creates a TSV where each row represents a species in the filtered dataset run through all of benchmark 1. The columns are as follows:
# taxonomic group	species ID	total sequences	num 1.0 ramps	num_1.0-fixed ramps	num 2.0 ramps	1.0 time	2.0 time	2.0-scores time

import sys
import os

def read_slurm_file(slurm_file_path, scores=False):
    with open(slurm_file_path, "r") as inf:
        lines = inf.readlines()
        if not lines[-1].startswith("Total time:"):
            print(f"ERROR: this slurm file may contain warnings or errors that will break this summary: {slurm_file_path}")
            return "", "", ""
        # get the lines where the important data is stored
        total_time_line = lines[-1].strip()
        if not scores:
            total_sequences_line = lines[-13].strip().lower()
            num_ramps_line = lines[-5].strip().lower()
        else:
            total_sequences_line = lines[-16].strip().lower()
            num_ramps_line = lines[-8].strip().lower()
        
    if not total_sequences_line.startswith("total valid sequences:") or not num_ramps_line.endswith("ramp sequences found"):
        print(f"ERROR: this slurm file may contain warnings or errors that will break this summary: {slurm_file_path}")
    
    total_sequences = total_sequences_line.split()[-1]
    num_ramps = num_ramps_line.split()[0]
    total_time = total_time_line.split()[-1]
    return total_sequences, num_ramps, total_time

if __name__ == "__main__":
    MEAN = sys.argv[1] if len(sys.argv) > 1 else "hmean"

    taxonomic_groups = ["archaea", "bacteria", "fungi", "invertebrate", "mammalia", "protozoa", "vertebrate-other", "viridiplantae"]
    versions = ["1.0", "1.0-fixed", "2.0"] # version 2.0 with scores is handled later in the code

    BASE_OUTPUT_FOLDER="../outputs"

    out_path = f"{BASE_OUTPUT_FOLDER}/benchmark1_summary_pt1-{MEAN}.tsv"

    # create a dictionary containing key value pairs for each of the TSV columns
    benchmark1_summary_dict = {}
    for version in versions:
        print(f"Processing version {version}...")
        for taxonomic_group in taxonomic_groups:
            print(f"\tProcessing taxonomic group {taxonomic_group}...")
            # for each slurm file
            slurm_folder_path = os.path.join(BASE_OUTPUT_FOLDER, version, MEAN, taxonomic_group, "slurm")
            if os.path.exists(slurm_folder_path):
                # get all the slurm file paths (excluding full group slurms)
                slurm_file_paths = [os.path.join(slurm_folder_path, file) for file in os.listdir(slurm_folder_path) if file.startswith(f"slurm-{version}-{MEAN}")]
                for slurm_file_path in slurm_file_paths:
                    # get the species ID from the file name
                    if "-scores" in slurm_file_path:
                        species_id = slurm_file_path.split("-")[-2]
                    else:
                        species_id = ".".join(slurm_file_path.split("-")[-1].split(".")[0:2])
                    if species_id not in benchmark1_summary_dict:
                        benchmark1_summary_dict[species_id] = {
                            "taxonomic group": taxonomic_group,
                            "species ID": species_id,
                            "total sequences": "",
                            "num 1.0 ramps": "",
                            "num 1.0-fixed ramps": "",
                            "num 2.0 ramps": "",
                            "1.0 time": "",
                            "2.0 time": "",
                            "diff 1.0 2.0 time": "",
                            "2.0-scores time": "NA"
                        }
                    # read relevant data from the slurm file
                    total_sequences, num_ramps, total_time = read_slurm_file(slurm_file_path, scores="-scores" in slurm_file_path)
                    if benchmark1_summary_dict[species_id]["total sequences"] == "":
                        benchmark1_summary_dict[species_id]["total sequences"] = total_sequences
                    if version == "1.0":
                        benchmark1_summary_dict[species_id]["num 1.0 ramps"] = num_ramps
                        benchmark1_summary_dict[species_id]["1.0 time"] = total_time
                    elif version == "1.0-fixed":
                        benchmark1_summary_dict[species_id]["num 1.0-fixed ramps"] = num_ramps
                    elif version == "2.0":
                        if "-scores" in slurm_file_path:
                            benchmark1_summary_dict[species_id]["2.0-scores time"] = total_time
                        else:
                            benchmark1_summary_dict[species_id]["num 2.0 ramps"] = num_ramps
                            benchmark1_summary_dict[species_id]["2.0 time"] = total_time
                            if benchmark1_summary_dict[species_id]["1.0 time"] != "" and total_time != "":
                                diff_time = float(benchmark1_summary_dict[species_id]["1.0 time"]) - float(total_time)
                                benchmark1_summary_dict[species_id]["diff 1.0 2.0 time"] = f"{diff_time:.2f}"

    
    # sort the dictionary by taxonomic group, then species ID
    tax_group_to_species_ids = {}
    for species_id, data in benchmark1_summary_dict.items():
        tax_group = data["taxonomic group"]
        if tax_group not in tax_group_to_species_ids:
            tax_group_to_species_ids[tax_group] = []
        tax_group_to_species_ids[tax_group].append(species_id)
    for tax_group in tax_group_to_species_ids:
        tax_group_to_species_ids[tax_group] = sorted(tax_group_to_species_ids[tax_group])
    
    # write the dictionary to a TSV
    print(f"Writing benchmark 1 summary to {out_path}...")
    with open(out_path, "w") as outf:
        outf.write("taxonomic group\tspecies ID\ttotal valid sequences\tnum 1.0 ramps\tnum 1.0-fixed ramps\tnum 2.0 ramps\t1.0 time\t2.0 time\t2.0-scores time\n")
        for tax_group in sorted(tax_group_to_species_ids.keys()):
            for species_id in tax_group_to_species_ids[tax_group]:
                data = benchmark1_summary_dict[species_id]
                outf.write(f"{data['taxonomic group']}\t{data['species ID']}\t{data['total sequences']}\t{data['num 1.0 ramps']}\t{data['num 1.0-fixed ramps']}\t{data['num 2.0 ramps']}\t{data['1.0 time']}\t{data['2.0 time']}\t{data['2.0-scores time']}\n")

print("done.")