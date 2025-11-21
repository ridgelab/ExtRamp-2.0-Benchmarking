# This script confirms that all jobs for a specific version completed successfully by:
# 1. Checking that the number of slurm files is equal to the number of filtered files
# 2. Checking that the last line of each slurm output file contains "Total time:"

VERSION=$1
MEAN=${2:-"hmean"} # the mean function to check
SCORES=${3:-"False"} # flag to check score slurms

if [ -z "$VERSION" ]; then
    echo "Version not specified!"
    exit 1
fi

BASE_IN_FOLDER="../inputs/filtered/"
BASE_OUT_FOLDER="../outputs/$VERSION/$MEAN"

all_passed=true

echo "Checking completion status for ExtRamp version $VERSION with mean '$MEAN'..."

# loop through all taxonomic groups (folders in BASE_OUT_FOLDER)
for TAXON_GROUP in $(ls $BASE_OUT_FOLDER); do
    # for testing, only check one taxonomic group
    # if [ "$TAXON_GROUP" != "vertebrate-other" ];
    # then
    #     continue
    # fi
    echo "Checking taxonomic group: $TAXON_GROUP"

    SLURM_FOLDER="$BASE_OUT_FOLDER/$TAXON_GROUP/slurm"
    if [ ! -d "$SLURM_FOLDER" ]; then
        echo -e "\tSlurm folder does not exist for $TAXON_GROUP, skipping..."
        continue
    fi

    # check that the number of slurm files matches the number of filtered files
    filtered_files=($(ls $BASE_IN_FOLDER/$TAXON_GROUP))
    slurm_files=($(find "$SLURM_FOLDER" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*.out" ! -name "*scores*"))
    # if SCORES is True and VERSION is 2.0, check score slurms
    if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
        slurm_files=($(find "$SLURM_FOLDER" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*-scores*.out"))
    fi
    if [ ${#slurm_files[@]} -ne ${#filtered_files[@]} ]; then
        echo -e "\t$TAXON_GROUP has ${#slurm_files[@]} slurm files, but should have ${#filtered_files[@]}"
        all_passed=false
    fi

    # loop through all slurm output files in the slurm folder
    # get the slurm files to check
    slurm_files=($(find "$SLURM_FOLDER" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*.out" ! -name "*scores*"))
    # if SCORES is True and VERSION is 2.0, check score slurms
    if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
        slurm_files=($(find "$SLURM_FOLDER" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*-scores*.out"))
    fi

    num_files=${#slurm_files[@]}
    file_num=0
    for SLURM_FILE in "${slurm_files[@]}"; do
        # check if the last line in the slurm file starts with "Total time:"
        LAST_LINE=$(tail -n 1 "$SLURM_FILE")
        if [[ ! $LAST_LINE == Total\ time:* ]]; then
            echo -e "\tJob failed: $SLURM_FILE; Last line: '$LAST_LINE'"
            all_passed=false
        fi
        file_num=$((file_num + 1))
        if (( file_num % 100 == 0 )); then
            echo -e "\t$file_num of $num_files"
        fi
    done
    echo -e "\t$file_num of $num_files"
done

if [ "$all_passed" = true ]; then
    echo "All jobs completed successfully!"
    exit 0
else
    echo "Some jobs failed or did not run. Please check the logs above."
    exit 1
fi
