#!/bin/bash
#SBATCH --time=05:00:00
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH -J "np_mem_ExtRamp"
#SBATCH --output=../outputs/np_mem/slurm/slurm-%x.%j.out

# This script tests whether the memory usage improvement in ExtRamp 2.0 is due to its usage of np arrays

lscpu
echo ""

TAXON_GROUP="mammalia"
SPECIES_ID="GCF_000001405.40"
MEAN="hmean"
IN_PATH="../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna"
OUT_PATH="../outputs/np_mem"

# create the output directory if it doesn't exist
if [ ! -d "$OUT_PATH" ]; then
  mkdir -p "$OUT_PATH"
fi

/usr/bin/time -v python ExtRamp2.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-2.0-ramps.fa
echo ""
echo ""
echo ""
/usr/bin/time -v python ExtRamp1.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-1.0-ramps.fa
echo ""
echo ""
echo ""
/usr/bin/time -v python ExtRamp-1.0-fixed-np.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-w9-1.0-fixed-np-ramps.fa
echo ""
echo "Finished np benchmark"