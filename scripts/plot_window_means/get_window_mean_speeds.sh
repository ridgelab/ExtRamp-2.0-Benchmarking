# This script runs ExtRamp 2.0 on a given species to create a window mean speeds file (used for plotting).

TAXON_GROUP=$1 # "mammalia"
SPECIES_ID=$2 # "GCF_000001405.40" (Homo sapiens)
MEAN="hmean"
IN_PATH="../../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna"
OUT_PATH="../../outputs/plot_window_means"

python ../ExtRamp2.0.py -v -t 4 -m $MEAN -w 9 -i $IN_PATH -o $OUT_PATH/$SPECIES_ID-$MEAN-2.0-ramps.fa -l $OUT_PATH/$SPECIES_ID-$MEAN-2.0-windowmeans.fa
