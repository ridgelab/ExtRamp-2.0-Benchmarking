#!/bin/bash
#SBATCH --time=05:00:00
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=16G
#SBATCH -J "window_means_ExtRamp"
#SBATCH --output=../outputs/window_means/slurm/slurm-%x.%j.out

# This script compares the speed and size improvements of the window means file created by ExtRamp 2.0 vs 1.0

lscpu
echo ""

TAXON_GROUP="mammalia"
SPECIES_ID="GCF_000001405.40"
MEAN="hmean"
IN_PATH="../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna"
OUT_PATH="../outputs/window_means"

# create the output directory if it doesn't exist
if [ ! -d "$OUT_PATH" ]; then
  mkdir -p "$OUT_PATH"
fi

/usr/bin/time -v python ExtRamp2.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-ramps.fa -l $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-windowmeans.fa
echo ""
echo ""
echo ""
/usr/bin/time -v python ExtRamp1.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-1.0-ramps.fa -l $OUT_PATH/$SPECIES_ID-$MEAN-w9-1.0-windowmeans.csv
echo ""
echo ""
echo ""
echo "Window mean file sizes:"
ls -lh $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-windowmeans.fa
ls -lh $OUT_PATH/$SPECIES_ID-$MEAN-w9-1.0-windowmeans.csv
echo ""
echo "Finished window means benchmark"