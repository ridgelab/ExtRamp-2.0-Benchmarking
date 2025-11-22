# This script gets the number and percent of sequences that differ between version 1.0 and version 2.0 and the number and percent
# of these sequences that 
# 1. cause a ramp status change
# 2. cause a ramp length change

import os

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

def write_and_log(message, logf):
    print(message)
    logf.write(message + "\n")

if __name__ == "__main__":
    output_log_path = "../outputs/length_vs_status.log"
    ramps_1_path = "../outputs/1.0/hmean/"
    ramps_2_path = "../outputs/2.0/hmean/"
    taxonomic_groups = ["archaea", "bacteria", "fungi", "invertebrate", "mammalia", "protozoa", "vertebrate-other", "viridiplantae"]
    
    species_to_paths = {}
    with open(output_log_path, "w") as outf:
        for group in taxonomic_groups:
            for file in os.listdir(ramps_2_path + "/" + group):
                species_id = file.split("-")[0]
                if (species_id.startswith("GCF_") or species_id.startswith("GCA_")) and species_id not in species_to_paths:
                    species_to_paths[species_id] = {}
                if file.endswith("ramps.fa"):
                    species_to_paths[species_id]["ramps_2.0"] = os.path.join(ramps_2_path, group, file)
            for file in os.listdir(ramps_1_path + "/" + group):
                species_id = file.split("-")[0]
                if (species_id.startswith("GCF_") or species_id.startswith("GCA_")) and species_id not in species_to_paths:
                    species_to_paths[species_id] = {}
                if file.endswith("ramps.fa"):
                    species_to_paths[species_id]["ramps_1.0"] = os.path.join(ramps_1_path, group, file)
        write_and_log(f"Found ramp results for {len(species_to_paths)} species.", outf)

        changed_status_header_num = 0
        changed_length_header_num = 0
        species_processed = 0
        for species_id, paths in species_to_paths.items():
            if "ramps_1.0" in paths and "ramps_2.0" in paths:
                ramps_1_lengths = get_ramp_lengths(paths["ramps_1.0"])
                ramps_2_lengths = get_ramp_lengths(paths["ramps_2.0"])

                changed_status_headers = set(ramps_1_lengths.keys()).symmetric_difference(set(ramps_2_lengths.keys()))
                changed_status_header_num += len(changed_status_headers)
                changed_length_headers = {header for header in set(ramps_1_lengths.keys()).intersection(set(ramps_2_lengths.keys())) if ramps_1_lengths[header] != ramps_2_lengths[header]}
                changed_length_header_num += len(changed_length_headers)
                species_processed += 1
                if species_processed % 100 == 0:
                    print(f"Processed {species_processed} species...")
            else:
                write_and_log(f"Missing files for species {species_id}, skipping...", outf)
        print(f"Processed a total of {species_processed} species.")
        
        percent_changed_status = (changed_status_header_num / (changed_status_header_num + changed_length_header_num)) * 100
        percent_changed_length = (changed_length_header_num / (changed_status_header_num + changed_length_header_num)) * 100

        write_and_log(f"Total sequences with changed ramp status: {changed_status_header_num} ({percent_changed_status:.2f}%)", outf)
        write_and_log(f"Total sequences with changed ramp length: {changed_length_header_num} ({percent_changed_length:.2f}%)", outf)