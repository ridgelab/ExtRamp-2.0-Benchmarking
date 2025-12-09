MEAN=${1:-"mean"}
TAXON_GROUP=${2:-"mammalia"}
SPECIES_ID=${3:-"GCF_000001405.40"}

/usr/bin/time -v python ExtRamp2.0.py -v -t 4 -m $MEAN -w 9 -i ../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna -o ../outputs/cumulative_sum/$SPECIES_ID-$MEAN-normal-w9-ramps.fa
echo ""
echo ""
/usr/bin/time -v python ExtRamp2.0-cumulative_sum.py -v -t 4 -m $MEAN -w 9 -i ../inputs/filtered/$TAXON_GROUP/$SPECIES_ID/cds_from_genomic.fna -o ../outputs/cumulative_sum/$SPECIES_ID-$MEAN-cumulative_sum-w9-ramps.fa
