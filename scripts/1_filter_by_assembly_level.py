# This script filters out species that don't have "chromosome" or "complete genome" assembly levels, moving all others to
# the low_assembly folder. It gets the assembly level information from the JSONL files downloaded from NCBI when the CDS database
# was built. Eukaryota is processed differently because it was downloaded as a whole group and while its species were split into
# subgroups, its JSONL file contains all species together.

import os
import json
import shutil

def get_species_ids_to_filter_out(jsonl_path):
    """
    Reads a JSONL file and returns a set of species IDs that do not have "chromosome" or "complete genome" assembly levels.
    Also returns the total number of species processed.
    """
    species_ids_to_filter_out = set()
    total_species = 0
    with open(jsonl_path) as inf:
        for line in inf:
            data = json.loads(line)
            assembly_level = data["assemblyInfo"]["assemblyLevel"].lower()
            if assembly_level not in ["complete genome", "chromosome"]:
                species_ids_to_filter_out.add(data["currentAccession"])
            total_species += 1
    return species_ids_to_filter_out, total_species

def find_existing_path(paths):
    """
    Finds and returns the first existing path in a list of paths.
    """
    for path in paths:
        if os.path.exists(path):
            return path
    return None

if __name__ == "__main__":
    # The location of the relevant JSON files
    original_data_path = "../inputs/original"
    # The two folders where species should be searched for
    filtered_data_path = "../inputs/filtered"
    filtered_out_data_path = "../inputs/filtered_out"
    # The location to move the species with low assembly levels
    low_assembly_data_path = "../inputs/low_assembly"
    # The name of the JSONL file in each taxonomic group folder
    file_name = "assembly_data_report.jsonl"
    
    # The taxonomic groups where the JSONL files are located
    taxonomic_groups = ["archaea", "bacteria", "eukaryota"]
    # The subgroups within eukaryota
    eukaryota_taxonomic_subgroups = ["fungi", "invertebrate", "mammalia", "protozoa", "vertebrate-other", "viridiplantae"]

    for group in taxonomic_groups:
        jsonl_path = f"{original_data_path}/{group}/{file_name}"
        species_ids_to_filter_out, total_species = get_species_ids_to_filter_out(jsonl_path)

        print(f"Group: {group}")
        print(f"\tTotal species: {total_species}")
        print(f"\tNumber of species to filter out: {len(species_ids_to_filter_out)}")
        print(f"\tSpecies left: {total_species - len(species_ids_to_filter_out)}")
        
        # Move the species folders to the new location
        if group == "eukaryota":
            for species_ID in species_ids_to_filter_out:
                # Check the filtered folder and the filtered_out folder for all subgroups
                possible_old_paths = [os.path.join(filtered_data_path, subgroup, species_ID) for subgroup in eukaryota_taxonomic_subgroups]
                possible_old_paths += [os.path.join(filtered_out_data_path, subgroup, species_ID) for subgroup in eukaryota_taxonomic_subgroups]
                old_path = find_existing_path(possible_old_paths)
                if old_path:
                    subgroup = old_path.split(os.sep)[-2]  # Extract subgroup from the path
                    new_path = os.path.join(low_assembly_data_path, subgroup, species_ID)
                    # Create the directory in low_assembly if it doesn't exist
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    # print(old_path, new_path)
                else:
                    print(f"WARNING: '{species_ID}' should be moved to '{low_assembly_data_path}', but not found in filtered or filtered_out folders for any eukaryota subgroup!")
        else:
            for species_ID in species_ids_to_filter_out:
                # Check the filtered folder and the filtered_out folder
                possible_old_paths = [os.path.join(filtered_data_path, group, species_ID), os.path.join(filtered_out_data_path, group, species_ID)]
                old_path = find_existing_path(possible_old_paths)
                if old_path:
                    new_path = os.path.join(low_assembly_data_path, group, species_ID)
                    # Create the directory in low_assembly if it doesn't exist
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    shutil.move(old_path, new_path)
                    # print(old_path, new_path)
                else:
                    print(f"WARNING: '{species_ID}' should be moved to '{low_assembly_data_path}', but not found in filtered or filtered_out folders for {group}!")
