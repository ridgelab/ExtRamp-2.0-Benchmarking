import sys

def getSeconds(time):
    items = time.split(":")
    if len(items) == 3:
        return round(int(items[0]) * 3600 + int(items[1]) * 60 + float(items[2]), 2)
    if len(items) == 2:
        return round(int(items[0]) * 60 + float(items[1]), 2)
    if len(items) == 1:
        return round(float(items[0]), 2)
    return 0

if __name__ == "__main__":
    slurmID = sys.argv[1]
    inPath = f"../outputs/time_mem/slurm/slurm-time_mem_ExtRamp.{slurmID}.out"
    skip = False
    version = ""
    taxonomicGroup = ""
    speciesID = ""
    runNumber = 0
    seqNum = ""
    time = ""
    memory = ""

    # "Version\tTaxonomicGroup\tSpeciesID\tRunNumber\tSequenceNumber\tTime\tMemory\n")

    results = []
    with open(inPath) as inf:
        mean = inf.readline().strip().split(" ")[-1]
        outPath = f"../outputs/time_mem/benchmark2_results_{mean}.tsv"
        for line in inf:
            line = line.strip()
            if line == "":
                continue
            elif "warmup" in line:
                skip = True
            elif line.startswith("Exit status:"):
                skip = False
                if runNumber != 0:
                    # add the outputline to the results
                    outputLine = f"{version}\t{taxonomicGroup}\t{speciesID}\t{runNumber}\t{seqNum}\t{time}\t{memory}"
                    results.append(outputLine)
            if not skip:
                if line.startswith("1.0") or line.startswith("2.0"):
                    items = line.split(" ")
                    if len(items) == 1:
                        skip = True
                    else:
                        version = items[0]
                        taxonomicGroup = items[1]
                        speciesID = items[2]
                        if taxonomicGroup == "taxonmicGroup" or taxonomicGroup == "Taxonomic":
                            skip = True
                        else:
                            if runNumber == 10:
                                runNumber = 0
                            runNumber += 1
                elif version == "1.0" and line.startswith("Total valid sequences:") or version == "2.0" and line.startswith("Total valid sequences:"):
                    seqNum = line.split(" ")[-1]
                elif line.startswith("Elapsed (wall clock) time"):
                    time = getSeconds(line.split(" ")[-1])
                elif "Maximum resident" in line:
                    memory = line.split(" ")[-1]
    with open(outPath, "w") as outf:
        outf.write("Version\tTaxonomicGroup\tSpeciesID\tRunNumber\tSequenceNumber\tTime\tMemory\n")
        for result in results:
            outf.write(result + "\n")

    print("done.")