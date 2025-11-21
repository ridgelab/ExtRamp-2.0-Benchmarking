# Gets all the slurm IDs for the 1.0 and 2.0 jobs run, then gets the job data for those job IDs

MEAN=${1:-"hmean"} # the mean function to use

output_path="../outputs/benchmark1_summary_pt2-${MEAN}.tsv"

function get_species_slurm_id {
    local filepath=$1
    # get the file name
    local filename="${filepath##*/}"
    # remove -scores from the file name if it exists
    if [ ! "$SCORES" = "True" ]; then
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

# Get the slurm IDs
slurm_ids=()
for VERSION in "1.0" "2.0"; do
    echo "Getting slurm IDs for version $VERSION..."
    BASE_OUTPUT_DIR="../outputs/$VERSION/$MEAN"
    for TAXON_GROUP in $(ls $BASE_OUTPUT_DIR); do
    # for TAXON_GROUP in "archaea"; do
        echo -e "\tChecking taxonomic group: $TAXON_GROUP"
        SLURM_PATH="$BASE_OUTPUT_DIR/$TAXON_GROUP/slurm"
        # get a list of all slurm files for the taxonomic group, version, and mean function
        slurm_files=($(find "$SLURM_PATH" -maxdepth 1 -type f -name "slurm-$VERSION-$MEAN-*.out" ! -name "*scores*"))

        for slurm_file in "${slurm_files[@]}"; do
            species_slurm_id=$(get_species_slurm_id "$slurm_file")
            IFS=' ' read -r species slurm_id <<< "$species_slurm_id"

            # add the slurm_id to the slurm_ids array
            slurm_ids+=("$slurm_id")
        done
    done
done

echo "Found ${#slurm_ids[@]} slurm IDs."

echo "Getting job data for slurm IDs..."
# clear the output file if it exists
> $output_path

# get job id data in batches of 100 to avoid command line length limits
for ((i=0; i<${#slurm_ids[@]}; i+=100)); do
    batch_ids=$(IFS=','; echo "${slurm_ids[*]:i:100}")
    # get the job data and append it to the output file
    sacct -j $batch_ids --format=JobID,JobName,MaxRSS --parsable2 --units=M >> $output_path
    echo -e "\t$((i+100)) slurm IDs processed"
done

python 5.2_clean_up_mem_benchmark1_results.py $output_path

echo "Output written to $output_path"