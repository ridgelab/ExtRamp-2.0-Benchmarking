# This scripts reads the numFiltered files to find X representative species for each taxon group
# The representative species are the ones with the least, median, and most sequences.

import sys
import os
import re
import math

# Get the scientific and common names for each species from the taxonomy files
def getTaxonGroupToSpeciesIDToTaxonomy(taxonomicGroups, taxonomyDir):
    taxonGroupToSpeciesIDToTaxonomy = {}
    for taxonGroup in taxonomicGroups:
        taxonomyFilePath = os.path.join(taxonomyDir, taxonGroup, f"{taxonGroup}Taxonomy.tsv")
        speciesIDToTaxonomy = {}
        if os.path.exists(taxonomyFilePath):
            with open(taxonomyFilePath, "r") as inf:
                header = inf.readline()
                for line in inf:
                    line = line.strip()
                    items = line.split("\t")
                    speciesID = items[0]
                    scientificName = items[-1].split("|")[-1]
                    commonName = items[2]
                    speciesIDToTaxonomy[speciesID] = (scientificName, commonName)
        taxonGroupToSpeciesIDToTaxonomy[taxonGroup] = speciesIDToTaxonomy
    return taxonGroupToSpeciesIDToTaxonomy

def getRepList(speciesIDToNumSequences, numSpeciesPerGroup):
    if numSpeciesPerGroup == 1:
        # If one species is requested, return the species with the most sequences
        return [max(speciesIDToNumSequences, key=speciesIDToNumSequences.get)]
    elif numSpeciesPerGroup >= len(speciesIDToNumSequences):
        # If there are fewer species than the requested number, return all species
        return sorted(speciesIDToNumSequences, key=speciesIDToNumSequences.get)
    elif numSpeciesPerGroup == 2:
        # If two species are requested, return the species with the least and most sequences
        return [min(speciesIDToNumSequences, key=speciesIDToNumSequences.get), max(speciesIDToNumSequences, key=speciesIDToNumSequences.get)]
    else:
        # Return the species that are evenly spaced in terms of number of sequences
        repSpeciesIDs = []
        sortedSpeciesIDs = sorted(speciesIDToNumSequences, key=speciesIDToNumSequences.get)
        step = math.ceil((len(speciesIDToNumSequences))/(numSpeciesPerGroup-1))
        stepNum = 0
        while stepNum < numSpeciesPerGroup - 1:
            repSpeciesIDs.append(sortedSpeciesIDs[stepNum * step])
            stepNum += 1
        repSpeciesIDs.append(max(speciesIDToNumSequences, key=speciesIDToNumSequences.get))
        return repSpeciesIDs

if __name__ == "__main__":
    # The number of species to select per taxon group
    numSpeciesPerGroup = sys.argv[1] if len(sys.argv) > 1 else 3
    # The file to print the ids of the representative species
    repSpeciesOutPath = sys.argv[2] if len(sys.argv) > 2 else "../outputs/representative_species.tsv"
    # The directory containing the numFiltered files
    numFilteredDir = sys.argv[3] if len(sys.argv) > 3 else "../outputs/"
    # The directory containing the taxonomy files
    taxonomyDir = sys.argv[4] if len(sys.argv) > 4 else "../outputs/taxonomy/"
    # The directory containing the filtered files
    filteredDataPath = sys.argv[5] if len(sys.argv) > 5 else "../inputs/filtered/"

    # Get the list of numFiltered files
    numFilteredFiles = os.listdir(numFilteredDir)
    numFilteredFiles = [file for file in numFilteredFiles if re.match(r"^numFiltered-[\w-]+\.tsv$", file)]
    taxonGroupToNumFilteredFile = {re.sub(r"^numFiltered-([\w-]+)\.tsv$", r"\1", file): file for file in numFilteredFiles}

    # Read in the taxonomy data for each taxon group
    taxonGroupToSpeciesIDToTaxonomy = getTaxonGroupToSpeciesIDToTaxonomy(taxonGroupToNumFilteredFile.keys(), taxonomyDir)

    # For each taxonGroup, open its file and get the representative species
    with open(repSpeciesOutPath, "w") as outf:
        outf.write("Taxonomic Group\tSpecies ID\tScientific Name\tCommon Name\tNumber of Filtered CDS Transcripts\n")
        for taxonGroup in sorted(taxonGroupToNumFilteredFile):
            numFilteredFile = taxonGroupToNumFilteredFile[taxonGroup]
            numFilteredFilePath = os.path.join(numFilteredDir, numFilteredFile)
            speciesIDToNumSequences = {}
            with open(numFilteredFilePath, "r") as inf:
                header = inf.readline()
                for line in inf:
                    line = line.strip()
                    items = line.split("\t")
                    speciesID = items[0]
                    percentFiltered = float(items[3])
                    # Only consider species with less than 10% of sequences filtered
                    if percentFiltered < 10.0:
                        # Only consider species in the filtered folder (not moved to low_assembly or filtered_out folders)
                        if os.path.exists(os.path.join(filteredDataPath, taxonGroup, speciesID)):
                            numSequences = int(items[-2])
                            speciesIDToNumSequences[speciesID] = numSequences

            # Get the representative species
            if speciesIDToNumSequences:
                repSpeciesIDs = getRepList(speciesIDToNumSequences, numSpeciesPerGroup)
                maxID = max(speciesIDToNumSequences, key=speciesIDToNumSequences.get)
                if maxID not in repSpeciesIDs:
                    print(f"Warning: The species with the most sequences ({maxID}) ({speciesIDToNumSequences[maxID]}) is not in the representative list for {taxonGroup}.")
                    exit(1)
                for repID in repSpeciesIDs:
                    repNumSequences = speciesIDToNumSequences[repID]
                    repScientificName, repCommonName = taxonGroupToSpeciesIDToTaxonomy[taxonGroup].get(repID, ("Unknown", "Unknown"))
                    outf.write(f"{taxonGroup}\t{repID}\t{repScientificName}\t{repCommonName}\t{repNumSequences}\n")

    print("done.")