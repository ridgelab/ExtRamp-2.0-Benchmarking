#!/bin/bash
#SBATCH --time=168:00:00
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "time_mem_ExtRamp"
#SBATCH --output=../outputs/time_mem/slurm/slurm-%x.%j.out

# This script runs each of the species in the representative species file 10 times each for both ExtRamp v1.0 and v2.0
# The hardware is warmed up using one run of each version using Homo sapiens input data. Runs are also spaced out by 
# 30 seconds to allow cooldown time.

MEAN=${1:-"hmean"}
# The path to the representative species TSV file created by 2_get_representative_species.py
REP_SPECIES_PATH=${2:-"../outputs/representative_species.tsv"}

if [ -z "$REP_SPECIES_PATH" ]; then
    echo "Usage: benchmarkExtRamp.sh <input tsv file> <mean>"
    exit 1
fi

echo "Starting ExtRamp time and memory benchmark for $MEAN"

lscpu
echo ""

function run_extramp {
    # makes the species output directory, deletes existing output files, runs ExtRamp 
    # with the given version, taxonomic group, and species ID, and waits 30 seconds
    VERSION=$1
    TAXON_GROUP=$2
    SPECIES_ID=$3
    MEAN=$4
    echo "$VERSION $TAXON_GROUP $SPECIES_ID $MEAN"

    SPECIES_OUT_PATH="../outputs/time_mem/$VERSION/$MEAN/$TAXON_GROUP/$SPECIES_ID/"
    # if the SPECIES_OUT_PATH doesn't exist, create it
    if [ ! -d $SPECIES_OUT_PATH ]; then
        mkdir -p $SPECIES_OUT_PATH;
    fi
    # delete any output files that exist in the directory
    rm -f $SPECIES_OUT_PATH/*.fa
    # run the program
    /usr/bin/time -v python ExtRamp$VERSION.py -v -t 4 -m $MEAN -w 9 -i ../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna -o $SPECIES_OUT_PATH/$SPECIES_ID-$MEAN-w9-ramps.fa
    sleep 30
    echo ""
    echo ""
}

# do a warmup run on Homo sapiens
echo "v1 warmup on mammalia GCF_000001405.40"
run_extramp "1.0" mammalia GCF_000001405.40 $MEAN
echo "v2 warmup on mammalia GCF_000001405.40"
run_extramp "2.0" mammalia GCF_000001405.40 $MEAN

# get taxonomic group and species ids from the input TSV file
while read line
do
    # skip the header line
    if [[ $line == Taxonomic* ]]; then
        continue
    fi
    TAXON_GROUP=$(echo $line | cut -f1 -d" ")
    SPECIES_ID=$(echo $line | cut -f2 -d" ")
    echo "$TAXON_GROUP $SPECIES_ID"
    # for each version
    for VERSION in 1.0 2.0; do
        for i in {1..10}; do
            run_extramp $VERSION $TAXON_GROUP $SPECIES_ID $MEAN
        done
    done
done < $REP_SPECIES_PATH