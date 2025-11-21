# This script combines the benchmark 1 summary files from step 5.1 and 5.2 into a single TSV file

import sys

MEAN = sys.argv[1] if len(sys.argv) > 1 else "hmean"

inpath1 = f"../outputs/benchmark1_summary_pt1-{MEAN}.tsv"
inpath2 = f"../outputs/benchmark1_summary_pt2-{MEAN}.tsv"
outpath = f"../outputs/benchmark1_summary_combined-{MEAN}.tsv"

species_id_to_data = {}
with open(inpath1, "r") as inf:
    header = inf.readline().strip()
    for line in inf:
        items = line.strip().split("\t")
        taxon_group = items[0]
        species_id = items[1]
        total_sequences = items[2]
        num_1_0_ramps = items[3]
        num_1_0_fixed_ramps = items[4]
        num_2_0_ramps = items[5]
        time_1_0 = items[6]
        time_2_0 = items[7]
        time_2_0_scores = items[8] if len(items) > 8 else "NA"
        species_id_to_data[species_id] = {
            "taxon_group": taxon_group,
            "total_sequences": total_sequences,
            "num_1_0_ramps": num_1_0_ramps,
            "num_1_0_fixed_ramps": num_1_0_fixed_ramps,
            "num_2_0_ramps": num_2_0_ramps,
            "time_1_0": time_1_0,
            "time_2_0": time_2_0,
            "time_2_0_scores": time_2_0_scores
        }

with open(inpath2, "r") as inf:
    header = inf.readline().strip()
    for line in inf:
        items = line.strip().split("\t")
        species_id = items[0]
        job_id1 = items[1]
        job_id2 = items[2]
        max_mem_1_0 = items[3]
        max_mem_2_0 = items[4]
        max_mem_diff = items[5]
        if species_id in species_id_to_data:
            species_id_to_data[species_id].update({
                "job_id1": job_id1,
                "job_id2": job_id2,
                "max_mem_1_0": max_mem_1_0,
                "max_mem_2_0": max_mem_2_0,
                "max_mem_diff": max_mem_diff
            })
        else:
            species_id_to_data[species_id] = {
                "job_id1": job_id1,
                "job_id2": job_id2,
                "max_mem_1_0": max_mem_1_0,
                "max_mem_2_0": max_mem_2_0,
                "max_mem_diff": max_mem_diff
            }

# Write out combined summary, sorted by taxon group, then species ID
taxon_group_to_species_ids = {}
for species_id, data in species_id_to_data.items():
    taxon_group = data["taxon_group"]
    if taxon_group not in taxon_group_to_species_ids:
        taxon_group_to_species_ids[taxon_group] = []
    taxon_group_to_species_ids[taxon_group].append(species_id)
for taxon_group in taxon_group_to_species_ids:
    taxon_group_to_species_ids[taxon_group] = sorted(taxon_group_to_species_ids[taxon_group])


with open(outpath, "w") as outf:
    outf.write("species_id\ttaxon_group\ttotal_valid_sequences\tnum1_ramps\tnum1_fixed_ramps\tnum2_ramps\ttime1(sec)\ttime2(sec)\ttime2_scores(sec)\ttimes_faster\tjob_id1\tjob_id2\tmax_mem_1(MB)\tmax_mem_2(MB)\tmax_mem_diff(MB)\n")
    for taxon_group in sorted(taxon_group_to_species_ids.keys()):
        species_ids = taxon_group_to_species_ids[taxon_group]
        for species_id in species_ids:
            data = species_id_to_data[species_id]
            taxon_group = data.get("taxon_group", "NA")
            total_sequences = data.get("total_sequences", "NA")
            num_1_0_ramps = data.get("num_1_0_ramps", "NA")
            num_1_0_fixed_ramps = data.get("num_1_0_fixed_ramps", "NA")
            num_2_0_ramps = data.get("num_2_0_ramps", "NA")
            time_1_0 = data.get("time_1_0", "NA")
            time_2_0 = data.get("time_2_0", "NA")
            time_2_0_scores = data.get("time_2_0_scores", "NA")
            times_faster = "NA"
            if time_1_0 != "NA" and time_2_0 != "NA":
                times_faster = f"{float(time_1_0) / float(time_2_0):.2f}"
            job_id1 = data.get("job_id1", "NA")
            job_id2 = data.get("job_id2", "NA")
            max_mem_1_0 = data.get("max_mem_1_0", "NA")
            max_mem_2_0 = data.get("max_mem_2_0", "NA")
            max_mem_diff = data.get("max_mem_diff", "NA")
            outf.write(f"{species_id}\t{taxon_group}\t{total_sequences}\t{num_1_0_ramps}\t{num_1_0_fixed_ramps}\t{num_2_0_ramps}\t{time_1_0}\t{time_2_0}\t{time_2_0_scores}\t{times_faster}\t{job_id1}\t{job_id2}\t{max_mem_1_0}\t{max_mem_2_0}\t{max_mem_diff}\n")

print(f"Combined benchmark 1 summary written to {outpath}")