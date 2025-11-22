#!/bin/bash
#SBATCH --time=00:30:00
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "scores_ExtRamp"
#SBATCH --output=../outputs/scores/slurm/slurm-%x.%j.out

# This script calculates scores for the Homo sapiens file

lscpu
echo ""

TAXON_GROUP="mammalia"
SPECIES_ID="GCF_000001405.40"
MEAN="hmean"
IN_PATH="../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna"
OUT_PATH="../outputs/scores"

# create the output directory if it doesn't exist
if [ ! -d "$OUT_PATH" ]; then
  mkdir -p "$OUT_PATH"
fi

/usr/bin/time -v python ExtRamp2.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-ramps.fa -y $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-scores.tsv
echo ""
echo "Finished scores benchmark"