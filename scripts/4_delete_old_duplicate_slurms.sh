# Finds species with multiple slurm files for a version and deletes the oldest one

TAXON_GROUP=$1 # the name of the folder the fasta files are in
VERSION=${2:-"2.0"} # the version of ExtRamp to run
MEAN=${3:-"hmean"} # the mean function to use
SCORES=${4:-"False"} # whether to output the scores file (only works for v2.0)

# quit if the taxonomic group is not supplied
if [ -z "${1}" ]; then
    echo "taxonomic group not set!"
    exit 1
fi

SLURM_PATH="../outputs/$VERSION/$MEAN/$TAXON_GROUP/slurm"

function get_species_slurm_id {
    local filepath=$1
    local SCORES=$2
    # get the file name
    local filename="${filepath##*/}"
    # remove -scores from the file name if it exists
    if [ "$SCORES" = "True" ]; then
        local species_slurm_id="${filename/-scores/}"
    else
        local species_slurm_id="$filename"
    fi
    # remove .out from the end
    species_slurm_id=${species_slurm_id%.out}
    # get everything after the last hyphen
    species_slurm_id=${species_slurm_id##*-}

    # split by '.'
    IFS='.' read -r species species_version slurm_id <<< "$species_slurm_id"
    species="$species.$species_version"
    
    echo $species $slurm_id
}

# get a list of all slurm files for the taxonomic group, version, and mean function
slurm_files=($(find "$SLURM_PATH" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*.out" ! -name "*scores*"))
# if SCORES is True and VERSION is 2.0, check score slurms
if [ "$SCORES" = "True" ] && [ "$VERSION" = "2.0" ]; then
    slurm_files=($(find "$SLURM_PATH" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*-scores*.out"))
fi

num_deleted=0

# create a dictionay to store the species and their corresponding slurm files
declare -A species_slurm_files
for slurm_file in "${slurm_files[@]}"; do
    species_slurm_id=$(get_species_slurm_id "$slurm_file" "$SCORES")
    IFS=' ' read -r species slurm_id <<< "$species_slurm_id"

    # if the species is not in the dictionary, add it, otherwise check which slurm file is older and delete it
    if [ -z "${species_slurm_files[$species]}" ]; then
        species_slurm_files["$species"]="$slurm_file"
    else
        # get which slurm file is the oldest and delete it
        species_slurm_id=$(get_species_slurm_id "${species_slurm_files[$species]}" "$SCORES")
        IFS=' ' read -r stored_species stored_slurm_id <<< "$species_slurm_id"
        # if stored_slurm_id is smaller, delete its file, otherwise delete the current slurm file
        if [ "$stored_slurm_id" -lt "$slurm_id" ]; then
            echo "Deleting ${species_slurm_files[$species]}"
            rm "${species_slurm_files[$species]}"
            # update the dictionary to the current slurm file
            species_slurm_files["$species"]="$slurm_file"
        else
            echo "Deleting $slurm_file"
            rm "$slurm_file"
        fi
        num_deleted=$((num_deleted + 1))
    fi
done

echo "Total old slurm files deleted: $num_deleted"
echo "Total left: ${#species_slurm_files[@]}"
