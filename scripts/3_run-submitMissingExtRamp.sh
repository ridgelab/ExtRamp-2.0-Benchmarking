#!/bin/bash

TAXON_GROUP=$1 # the name of the folder the fasta files are in
VERSION=${2:-"2.0"} # the version of ExtRamp to run
MAX_TIME=${3:-"00:05:00"} # the max time for each fasta file to run
MEAN=${4:-"hmean"} # the mean function to use
SCORES=${5:-"False"} # whether to output the scores file (only works for v2.0)
THIS_MAX_TIME=${6:-"02:00:00"} # the max time to create .sh files and run each for all fastas in the folder

# quit if the taxonomic group is not supplied
if [ -z "${1}" ]; then
    echo "taxonomic group not set!"
    exit 1
fi

BASE_SCRIPT_FOLDER=./run-scripts/$VERSION/$MEAN/$TAXON_GROUP
mkdir -p "$BASE_SCRIPT_FOLDER"
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    scriptFileName=$BASE_SCRIPT_FOLDER/${VERSION}-$MEAN-${TAXON_GROUP}-missing-scores.sh
else
    scriptFileName=$BASE_SCRIPT_FOLDER/${VERSION}-$MEAN-${TAXON_GROUP}-missing.sh
fi

BASE_OUT_FOLDER="../outputs/$VERSION/$MEAN/$TAXON_GROUP"

echo "#!/bin/bash" > $scriptFileName
echo "#SBATCH --time=$THIS_MAX_TIME" >> $scriptFileName
echo "#SBATCH --ntasks=1" >> $scriptFileName
echo "#SBATCH --nodes=1" >> $scriptFileName
echo "#SBATCH --mem-per-cpu=1G" >> $scriptFileName
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    echo "#SBATCH -J \"run-${VERSION}-${MEAN}-${TAXON_GROUP}-missing-scores\"" >> $scriptFileName
else
    echo "#SBATCH -J \"run-${VERSION}-${MEAN}-${TAXON_GROUP}-missing\"" >> $scriptFileName
fi
echo "#SBATCH --output=$BASE_OUT_FOLDER/slurm/slurm-%x.%j.out" >> $scriptFileName
echo "" >> $scriptFileName

echo "directory=../inputs/filtered/$TAXON_GROUP/*" >> $scriptFileName

echo "for dir in \$directory/; do" >> $scriptFileName
echo -e "\tcds=\$(basename "\$dir")" >> $scriptFileName
# if the output file doesn't exist, run ExtRamp on it
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    echo -e "\tif [ ! -f '$BASE_OUT_FOLDER/\${cds}/\${cds}-hmean-w9-ramps.fa' ] || [ ! -f '$BASE_OUT_FOLDER/\${cds}/\${cds}-hmean-w9-ramps-scores.tsv' ]; then" >> $scriptFileName
else
    echo -e "\tif [ ! -f '$BASE_OUT_FOLDER/\${cds}/\${cds}-hmean-w9-ramps.fa' ]; then" >> $scriptFileName
fi
echo -e "\t\techo \$cds" >> $scriptFileName
echo -e "\t\tbash 3_run-submitOneExtRamp.sh \$cds $TAXON_GROUP $VERSION \"$MAX_TIME\" $MEAN $SCORES" >> $scriptFileName
echo -e "\tfi" >> $scriptFileName

echo "done" >> $scriptFileName
echo "echo \"done.\"" >> $scriptFileName

sbatch $scriptFileName