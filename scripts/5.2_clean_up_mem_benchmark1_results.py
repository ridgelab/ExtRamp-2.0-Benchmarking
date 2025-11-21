# Cleans up the speed_mem_benchmark1.txt file

import sys

inpath = sys.argv[1] if len(sys.argv) > 1 else "../outputs/benchmark1_summary_pt2-hmean.tsv"

job_id_to_results = {}
with open(inpath, "r") as inf:
    for line in inf:
        if line.startswith("JobID"):
            continue
        items = line.strip().split("|")
        job_id = items[0].split(".")[0]
        if job_id not in job_id_to_results:
            job_id_to_results[job_id] = {"species_id": "NA", "version": "NA", "max_rss": "NA"}
        job_name = items[1]
        if "-" in job_name:
            job_name_items = job_name.split("-")
            version = job_name_items[0]
            species_id = job_name_items[-1]
            job_id_to_results[job_id]["version"] = version
            job_id_to_results[job_id]["species_id"] = species_id
        elif job_name == "batch":
            max_rss=float(items[2][:-1])  # remove trailing M
            job_id_to_results[job_id]["max_rss"] = max_rss

species_id_to_results = {}
for job_id, results in job_id_to_results.items():
    species_id = results["species_id"]
    version = results["version"]
    max_rss = results["max_rss"]
    if species_id not in species_id_to_results:
        species_id_to_results[species_id] = {}
    species_id_to_results[species_id][version] = {"job_id": job_id, "max_rss": max_rss}

# Write out cleaned results over input file
with open(inpath, "w") as outf:
    outf.write("species_id\tjob_id1\tjob_id2\tmax_mem1(M)\tmax_mem2(M)\tmax_mem_diff(M)\n")
    for species_id in sorted(species_id_to_results.keys()):
        job_id1 = "NA"
        job_id2 = "NA"
        max_rss1 = "NA"
        max_rss2 = "NA"
        max_rss_diff = "NA"

        if "1.0" in species_id_to_results[species_id]:
            job_id1 = species_id_to_results[species_id]["1.0"]["job_id"]
            max_rss1 = species_id_to_results[species_id]["1.0"]["max_rss"]
        if "2.0" in species_id_to_results[species_id]:
            job_id2 = species_id_to_results[species_id]["2.0"]["job_id"]
            max_rss2 = species_id_to_results[species_id]["2.0"]["max_rss"]
        
        if "1.0" in species_id_to_results[species_id] and "2.0" in species_id_to_results[species_id]:
            max_rss_diff = max_rss1 - max_rss2

        outf.write(f"{species_id}\t{job_id1}\t{job_id2}\t{max_rss1}\t{max_rss2}\t{max_rss_diff:.2f}\n")
print("Finished cleaning up memory benchmark results.")
