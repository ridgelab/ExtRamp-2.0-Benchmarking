#!/bin/bash

ID=$1
TAXON_GROUP=$2 # the taxonomic group to run
VERSION=${3:-"2.0"} # the version of ExtRamp to run
MAX_TIME=${4:-"00:05:00"} # the max time for the species to run
MEAN=${5:-"hmean"} # the mean function to use
SCORES=${6:-"False"} # whether to output the scores file (only works for v2.0)

# quit if the ID or TAXON_GROUP is not supplied
if [ -z "${1}" ] || [ -z "${2}" ]; then
    echo "Species ID or taxonomic group not set!"
    exit 1
fi

BASE_SCRIPT_FOLDER=./run-scripts/$VERSION/$MEAN/$TAXON_GROUP
mkdir -p "$BASE_SCRIPT_FOLDER"
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    scriptFileName=$BASE_SCRIPT_FOLDER/$VERSION-$MEAN-$ID-scores.sh
else
    scriptFileName=$BASE_SCRIPT_FOLDER/$VERSION-$MEAN-$ID.sh
fi

BASE_OUT_FOLDER="../outputs/$VERSION/$MEAN/$TAXON_GROUP"

echo "#!/bin/bash" > $scriptFileName
echo "#SBATCH --time=$MAX_TIME" >> $scriptFileName
echo "#SBATCH --ntasks=4" >> $scriptFileName
echo "#SBATCH --nodes=1" >> $scriptFileName
echo "#SBATCH --mem-per-cpu=2G" >> $scriptFileName
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    echo "#SBATCH -J \"$VERSION-$MEAN-$ID-scores\"" >> $scriptFileName
else
    echo "#SBATCH -J \"$VERSION-$MEAN-$ID\"" >> $scriptFileName
fi
echo "#SBATCH --output=$BASE_OUT_FOLDER/slurm/slurm-%x.%j.out" >> $scriptFileName
echo "" >> $scriptFileName

pythonStr="python ExtRamp$VERSION.py -v -t 4 -m $MEAN -w 9 -i ../inputs/filtered/$TAXON_GROUP/$ID/cds_from_genomic.fna -o $BASE_OUT_FOLDER/$ID-$MEAN-w9-ramps.fa"
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    pythonStr="$pythonStr -y $BASE_OUT_FOLDER/$ID-$MEAN-w9-scores.tsv"
fi
echo $pythonStr >> $scriptFileName

sbatch $scriptFileName