# ExtRamp 2.0 Benchmarking Code

This README documents the benchmarking process we used to benchmark ExRamp 2.0 compared to ExtRamp 1.0. Each step contains an explanation, followed by the command(s) we ran to complete the step. The commands were all run within the directory that contains their script.

# Figures
The following are the figures in the paper and scripts used to generate them. All figures are in png and tif formats:
* [Figure 1](./outputs/time_mem/num_seq_to_time_mem-hmean.png) --- [Figure 1 Script](./scripts/8_process_benchmark2_data.py)
* Supplementary Figure 1 --- created in Lucidchart
* Supplementary Figure 2 --- created in Lucidchart
* [Supplementary Figure 3](./scripts/other-figures/hypothetical_plots.png) --- [Supplementary Figure 3 Script](./scripts/other-figures/hypothetical_plots.py)
* Supplementary Figure 4 [gmean](./outputs/time_mem/num_seq_to_time_mem-gmean.png), [mean](./outputs/time_mem/num_seq_to_time_mem-mean.png), and [median](./outputs/time_mem/num_seq_to_time_mem-median.png) --- [Supplementary Figure 4 Script](./scripts/8_process_benchmark2_data.py)
* [Supplementary Figure 5](./outputs/benchmark1_differences.png) --- [Supplementary Figure 5 Script](6.3_visualize_diffs.py)
* [Supplementary Figure 6](./outputs/scores/vulnerable_sequence_scores_mammalia.png) --- [Supplementary Figure 6 Script](./scripts/10_plot_vulnerable_sequence_scores_mammalia.py)
* [Supplementary Figure 7](./outputs/scores/ramp_strength_robustness_combined.png) --- [Supplementary Figure 7 Script](./scripts/10_analyze_scores.py)

# Links
ExtRamp 2.0 Paper- coming soon!\
[ExtRamp 2.0 Release GitHub](https://github.com/ridgelab/ExtRamp-2.0)

# REQUIREMENTS
These benchmarking scripts were developed and run in Python version 3.12.2.

Required libraries are available in the [requirements.txt](./scripts/requirements.txt) file. Use the following command to install them:
```
pip3 install -r requirements.txt
```

# Data Collection and Processing
We prepared a database of all available NCBI CDS FASTAs for species with reference genomes using the steps outlined in the [NCBI-CDS-Database-Builder](https://github.com/MattCloward/NCBI-CDS-Database-Builder) GitHub repository. The code from that repository was downloaded and placed in the [./scripts/NCBI-CDS-Database-Builder/](./scripts/NCBI-CDS-Database-Builder/) folder and all database-building scripts were run sequentially from that folder. All data was downloaded on Sep 3, 2025 using version 18.6.0 of NCBI's datasets command-line tool.

## Filter Out Incomplete Assemblies
[1_filter_by_assembly_level.py](./scripts/1_filter_by_assembly_level.py) moves all species to the [low_assembly](./inputs/low_assembly/) folder whose assembly level is not "chromosome" or "complete genome" (ie: "scaffold" or "contig"). ExtRamp works best on full genomes, so this step filters out species whose genomes are incomplete.
```
python 1_filter_by_assembly_level.py
```

## Get New Species Counts
After filtering out lower quality assemblies, we reran the `6_get_num_database_species.sh' file from the [NCBI-CDS-Database-Builder](https://github.com/MattCloward/NCBI-CDS-Database-Builder) GitHub repository to get an updated count of species left after all filtering steps. This file is saved to [num_database_species.tsv](./outputs/num_database_species.tsv) and is Supplementary Table 1.
```
bash 6_get_num_database_species.sh
```

## Get Representative Species
[2_get_representative_species.py](./scripts/2_get_representative_species.py) creates a [representative_species.tsv](./outputs/representative_species.tsv) file (Supplementary Table 2) containing the species IDs, scientific names, common names (if available), and number of sequences for the species with the least, median, and most sequences for each taxonomic group. The script assumes that the taxonomic data for all species in the database have already been obtained as detailed in the README for the [NCBI-CDS-Database-Builder](https://github.com/MattCloward/NCBI-CDS-Database-Builder) repository.
```
python 2_get_representative_species.py
```

# Benchmarks
We ran two benchmarks to compare ExtRamp 1.0 and 2.0.

## Output Testing Benchmark
In the first benchmark, we ran the following versions of ExtRamp:
* ExtRamp 1.0
* ExtRamp 1.0-fixed (a 1.0 version that fixes a bug where the last window mean was not considered)
* ExtRamp 1.0-fixed-truncated ("truncated" means all window means were truncated to the 13th decimal place)
* ExtRamp 2.0
* ExtRamp 2.0-truncated (again, "truncated" means window means were truncated to the 13th decimal place) and
* ExtRamp 2.0 with scores
We ran each of these programs on our filtered dataset to compare outputs and get an estimate of time required for each program. In this benchmark, we did not control what hardware each of the slurm jobs was run on. The commands run for this step can be found in [3_commands.txt](./scripts/3_commands.txt).

[3_run-submitTaxonGroupExtRamp.sh](./scripts/3_run-submitTaxonGroupExtRamp.sh) creates and runs a slurm job for the specified taxon group. This slurm job runs [3_run-submitOneExtRamp.sh](./scripts/3_run-submitOneExtRamp.sh) for each species in the specified taxon group, which in turn creates and runs a slurm job that runs the specified ExtRamp version with the given middle function. If the output files for any species are deleted or fail to generate, [3_run-submitMissingExtRamp.sh](./scripts/3_run-submitMissingExtRamp.sh) can be run with similar syntax as [3_run-submitTaxonGroupExtRamp.sh](./scripts/3_run-submitTaxonGroupExtRamp.sh) to find and run the missing species for the given taxon group. This script does not work if the output files are partially generated, so the next step handles that case.

### Confirm Job Completion
[4_confirm_completion.sh](./scripts/4_confirm_completion.sh) checks that all jobs completed successfully. It takes in a version, mean function, and score flag, checking all corresponding slurm files to confirm they end with a line starting with "Total time:". The commands run for this step can be found in [4_commands.txt](./scripts/4_commands.txt).
```
bash 4_confirm_completion.sh
```
If any jobs were found to have failed in this step (due to running out of time), we reran them individially with more time using [3_run-submitOneExtRamp.sh](./scripts/3_run-submitOneExtRamp.sh). For example:
```
bash 3_run-submitOneExtRamp.sh GCF_000001405.40 mammalia 1.0 02:00:00 hmean False
```
We then deleted the failed slurm files using [4_delete_old_duplicate_slurms.sh](./scripts/4_delete_old_duplicate_slurms.sh). It takes a taxonomic group, version, mean, and scores flag and finds when two slurms exist for a single species and deletes the older one, keeping the file with the larger slurm ID. For example, if one or more mammalia jobs for version 1.0 were run again, this command would delete the older slurm files:
```
bash 4_delete_old_duplicate_slurms.sh mammalia 1.0 hmean False
```

### Summarize Results
[5.1_get_benchmark1_results.py](./scripts/5.1_get_benchmark1_results.py) and [5.2_get_mem_benchmark1_results.sh](./scripts/5.2_get_mem_benchmark1_results.sh) both create a half of the summarized results, pt1 and pt2 respectively. Part 1 reads from the slurm files to get, for each species, the total valid sequences, the number of ramps for v1.0, v1.0-fixed, and v2.0, and the time taken to run v1.0, v2.0 and v2.0 with scores. Part 2 uses the "sacct" command to get, for each species, the max memory used for v1.0 and v2.0 and the difference in max memory used between both versions. In part 2, [5.2_get_mem_benchmark1_results.sh](./scripts/5.2_get_mem_benchmark1_results.sh) calls [5.2_clean_up_mem_benchmark1_results.py](./scripts/5.2_clean_up_mem_benchmark1_results.py) to clean up the results and put them in TSV format. The results can be found in the following two files:\
[benchmark1_summary_pt1-hmean.tsv](./outputs/benchmark1_summary_pt1-hmean.tsv)\
[benchmark1_summary_pt2-hmean.tsv](./outputs/benchmark1_summary_pt2-hmean.tsv).

These scripts are run like so:
```
python 5.1_get_benchmark1_results.py hmean
bash 5.2_get_mem_benchmark1_results.sh hmean
```

[5.3_combine_benchmark1_summaries.py](./scripts/5.3_combine_benchmark1_summaries.py) then combines the results of both parts of the summary into one file: [benchmark1_summary_combined-hmean.tsv](./outputs/benchmark1_summary_combined-hmean.tsv)
```
python 5.3_combine_benchmark1_summaries.py hmean
```

### Determine Difference Causes
[6.1_summarize_diff_causes.py](./scripts/6.1_summarize_diff_causes.py) counts the number of differences in the results between version 1.0 and 2.0 across all species in the dataset and determines the reason for each difference. The results are written to [benchmark1_difference_explanation-hmean.tsv](./outputs/benchmark1_difference_explanation-hmean.tsv)
The reason for differences in outputs between ExtRamp 1.0 and 2.0 are:
1. A bug in ExtRamp 1.0 that excluded the last window mean in calculations and
2. Rounding differences in the 15th or 16th decimal place.

The script first finds all differences in output between v1.0 and v2.0. This includes headers not shared between the results as well as ramp sequences that aren't the same between shared headers. It then finds all headers that are different due to reason #1 by finding all differences in output between v1.0 and v1.0-fixed. For the remaining differences, the results between v1.0-fixed-truncated and v2.0-truncated are compared and if differences are resolved between these versions, the differences are due to rounding errors. The results are written to [benchmark1_difference_explanation-hmean.tsv](./outputs/benchmark1_difference_explanation-hmean.tsv)
This script may take a while to run since it analyzes all outputs from the benchmark!
```
python 6.1_summarize_diff_causes.py hmean
```
The above script fails to explain a small handful of differences, which are output to [unexplained_differences.tsv](./outputs/unexplained_differences.tsv). These are further analyzed by [6.2_explain_unexplained_differences.py](./scripts/6.2_explain_unexplained_differences.py). This script reads in the [unexplained_differences.tsv](./outputs/unexplained_differences.tsv) and runs ExtRamp v1 and v2 on each header in the file, additionally saving the windowMeans using the `-l` parameter. To save time, v2 creates a wij file and v1 uses it to only run on headers in the [unexplained_differences.tsv](./outputs/unexplained_differences.tsv) file. The script compares the v1 and v2 window means at different critical positions to confirm that the remaining differences are also due to rounding differences. The results from the [benchmark1_difference_explanation-hmean.tsv](./outputs/benchmark1_difference_explanation-hmean.tsv) are updated and written to [benchmark1_difference_explanation-final-hmean.tsv](./outputs/benchmark1_difference_explanation-final-hmean.tsv).
```
python 6.2_explain_unexplained_differences.py
```
Finally, the results are visualized in pie charts using [6.3_visualize_diffs.py](./scripts/6.3_visualize_diffs.py), written to [benchmark1_differences.png](./outputs/benchmark1_differences.png), which is Supplementary Figure 5.
```
python 6.3_visualize_diffs.py
```
[6.4_summarize_diff_causes_species.py](./scripts/6.4_summarize_diff_causes_species.py) contains duplicate code from [6.1_summarize_diff_causes.py](./scripts/6.1_summarize_diff_causes.py) and is used to get species-specific differences between v1 and v2. We used it to get the number of ramps that differ between ExtRamp versions for [*Homo sapiens*](./outputs/benchmark1_difference_explanation-GCF_000001405.40-mammalia-hmean.tsv).
```
python 6.4_summarize_diff_causes_species.py mammalia GCF_000001405.40
```
[6.5_length_vs_status.py](./scripts/6.5_length_vs_status.py) reads all the ExtRamp results for v1 and v2, writing to [a log file](./outputs/length_vs_status.log) the number and percent of sequences whose ramp status differed and whose ramp length differed between versions.
```
python 6.5_length_vs_status.py
```

## Speed and Memory Benchmark
In the second benchmark, we ran only the representative species through ExtRamp v1 and v2, recording the time and max memory each used. We made sure to run these all on the same BYU supercomputer hardware, one slurm job for each of the mean functions ExtRamp supports (harmonic mean "hmean", geometric mean "gmean", arithmetic mean "mean", and median). Each representative species was run 10 times for each version, with 30 second breaks between each run. The system was warmed up using a run on *Homo sapiens* for both versions. These benchmarks were run using the [7_speed_mem_benchmark.sh](./scripts/7_speed_mem_benchmark.sh) script:
```
sbatch 7_speed_mem_benchmark.sh hmean
sbatch 7_speed_mem_benchmark.sh gmean
sbatch 7_speed_mem_benchmark.sh mean
sbatch 7_speed_mem_benchmark.sh median
```

### Processing Benchmark2 Results
The results of each of the mean benchmarks are read from the slurm files using the [8_get_benchmark2_data.py](./scripts/8_get_benchmark2_data.py) script and the outputs are written to the time_mem directory in the outputs directory in this format: `../outputs/time_mem/benchmark2_results_{MEAN}.tsv`. Ex: [benchmark2_results_hmean.tsv](./outputs/time_mem/benchmark2_results_hmean.tsv). Each line represents the results of one run of ExtRamp, either v1 or v2.
```
# Run this command for each of the mean slurms, replacing <slurm_id> with the slurm id of the slurm file.
python 8_get_benchmark2_data.py <slurm_id>
# ex:
python 8_get_benchmark2_data.py 7058404
```

[8_process_benchmark2_data.py](./scripts/8_process_benchmark2_data.py) creates three plots and summary stats for each mean function. Two plots compare time and memory to the number of sequences between v1 and v2 and the third combines those two plots. The summary file summarizes the file generated by [8_get_benchmark2_data.py](./scripts/8_get_benchmark2_data.py) so that each line represents a species and times and memory usage are averaged across all runs. All three outputs for each are written to the time_mem outputs directory. Here are the outputs for hmean: [Hmean Time Plot](./outputs/time_mem/num_seq_to_time-hmean.png), [Hmean Memory Plot](./outputs/time_mem/num_seq_to_mem-hmean.png), [Hmean Time and Memory Plot](./outputs/time_mem/num_seq_to_time_mem-hmean.png) (Figure 1), [Hmean Summary Stats](./outputs/time_mem/benchmark2_summary_hmean.tsv). The time and memory plots for [gmean](./outputs/time_mem/num_seq_to_time_mem-gmean.png), [mean](./outputs/time_mem/num_seq_to_time_mem-mean.png), and [median](./outputs/time_mem/num_seq_to_time_mem-median.png) are Supplementary Figure 4.
```
python 8_process_benchmark2_data.py
```

## Numpy Array Benchmark
[9_np_mem_benchmark.sh](./scripts/9_np_mem_benchmark.sh) tests wether the memory usage improvement in ExtRamp 2.0 are solely due to its use of numpy arrays. It does this by running three versions of ExtRamp on the *Homo sapiens* input data: [2.0](./scripts/ExtRamp2.0.py), [1.0](./scripts/ExtRamp1.0.py), and [a version of 1.0 that uses numpy arrays](./scripts/ExtRamp-1.0-fixed-np.py). The max memory usage for each run is printed to the slurm output log using /usr/bin/time.
```
mkdir -p ../outputs/np_mem/slurm
sbatch 9_np_mem_benchmark.sh
```

## Window Means Benchmark
[9_windowmeans_benchmark.sh](./scripts/9_windowmeans_benchmark.sh) tests the difference in the size of the window means file and the time required to create it using ExtRamp 2.0 and 1.0. It creates window mean files (option -l) using ExtRamp 2.0 and 1.0 and prints the resulting file sizes. The difference in time taken to create them is also written as a part of the -v verbose ExtRamp option.
```
mkdir -p ../outputs/window_means/slurm
sbatch 9_windowmeans_benchmark.sh
```

## Scores Benchmark
[10_scores_benchmark.sh](./scripts/9_scores_benchmark.sh) calculates ramp scores for the *Homo sapiens* input data, printing out the time it takes to calculate and write them to file.
```
mkdir -p ../outputs/scores/slurm
sbatch 10_scores_benchmark.sh
```
These scores are then analyzed by [10_analyze_scores.py](./scripts/10_analyze_scores.py), which plots distributions of ramp strength and ramp robustness scores for *Homo sapiens*. It also plots ramp strength against ramp robustness for *Homo sapiens*, showing that they are highly coorelated, but not the same. These plots are saved to the [scores output folder](./outputs/scores/). [ramp_strength_robustness_combined.png](./outputs/scores/ramp_strength_robustness_combined.png) is Supplementary Figure 7.
```
python 10_analyze_scores.py
```

[10_plot_vulnerable_sequence_scores_mammalia.py](./scripts/10_plot_vulnerable_sequence_scores_mammalia.py) creates plots similar to [10_analyze_scores.py](./scripts/10_analyze_scores.py), except that it plots scores for all mammalian sequences in the dataset instead. The graphs compare the scores for the sequences whose ramp status changed between ExtRamp versions to those that did not.\
In the [ramp strength vs ramp robustness score plot](./outputs/scores/vulnerable_sequence_scores_mammalia.png), Supplementary Figure 6, blue points are sequences that didn't change status, red points are sequences that changed status because of the last window mean exclusion bug, and yellow points are sequences that changed status due to differences in rounding between ExtRamp versions.\
In the [strength histogram](./outputs/scores/vulnerable_sequence_strength_histogram_mammalia.png) and [robustness histogram](./outputs/scores/vulnerable_sequence_robustness_histogram_mammalia.png) plots, the blue distribution represents the sequences that did not change ramp status between versions while the red distribition represents the sequences that did change ramp status between versions.
```
python 10_plot_vulnerable_sequence_scores_mammalia.py
```

## Cumulative Sum Benchmark
Late in the development of ExtRamp 2.0, it was suggested to us that we use a cumulative sum for computing the sliding window means instead of 1D convolutions. 1D convolutions are faster than for loops, not because they perform fewer operations, but because NumPy is optimized and compiled in C. Cumulative sum sliding windows have the potential to drastically reduce runtime because they perform so many fewer operations. This implementation is found in [ExtRamp2.0-cumulative_sum.py](./scripts/ExtRamp2.0-cumulative_sum.py) and benchmarked in [11_cumulative_sum.sh](./scripts/11_cumulative_sum.sh). The benchmark script runs the normal version of ExtRamp 2.0, followed by the cumulative sum version, printing out the time taken, [available here](./outputs/cumulative_sum/cumulative_sum.log). The most important time to compare between versions is on the lines that say: "Isolating ramp sequences... took:". Notably, despite the cumulative sum version doing fewer operations it both implementations take about the same amount of time and memory. There is potential for greater algorithm optimization using cumulative sums or rolling sums, but we opted not to explore these optimizations further in this work since the bottleneck of ExtRamp is no longer in sliding window mean calculations.
```
bash 11_cumulative_sum.sh > ../outputs/cumulative_sum/cumulative_sum.log 2>&1
```

# Hypothetical Plot
[hypothetical_plots.py](./scripts/other-figures/hypothetical_plots.py) plots [hypothetical_plots.png](./scripts/other-figures/hypothetical_plots.png) which is Supplementary Figure 3. It is used to help explain how ramp strength and ramp robustness scores are calculated. It is run from the ./scripts/other-figures/ folder.
```
python hypothetical_plots.py
```

# Window Mean Plotting
The window means of any sequence in the database can be plotted using the two scripts in the [scripts/plot_window_means](./scripts/plot_window_means/) directory. First, [get_window_mean_speeds.sh](./scripts/plot_window_means/get_window_mean_speeds.sh) is used to write a window mean speeds file for a given species.
```
bash plot_window_means/get_window_mean_speeds.sh <taxonomic group> <species ID>
```
Then, [plot_window_mean_speeds.py](./scripts/plot_window_means/plot_window_mean_speeds.py) is used to plot the window mean speeds, given a species ID and sequence header.
```
python plot_window_mean_speeds.py <species ID> <header>
```
## Examples
There were two outliers of interest on the [vulnerable ramp strength vs robustnesss score graph](./outputs/scores/vulnerable_sequence_scores_mammalia.png). 

We plotted the red outlier close to x=-2.7 [here](./outputs/plot_window_means/windowMeans-GCF_949987515.2-LOC132419140.png) using the following commands:
```
bash plot_window_means/get_window_mean_speeds.sh mammalia GCF_949987515.2
python plot_window_mean_speeds.py GCF_949987515.2 ">lcl|NC_082684.1_cds_XP_059859157.1_6662 [gene=LOC132419140] [db_xref=GeneID:132419140] [protein=variant surface antigen E-like] [protein_id=XP_059859157.1] [location=complement(177448856..177449518)] [gbkey=CDS]"
```
The high ramp strength score is clearly caused by the addition of the last window mean in the calculations, which is not interpreted by ExtRamp 1.0.

We plotted the yellow outlier on the top right of the plot [here](./outputs/plot_window_means/windowMeans-GCF_903995435.1-SIX5.png) using the following commands:
```
bash plot_window_means/get_window_mean_speeds.sh mammalia GCF_903995435.1
python plot_window_mean_speeds.py GCF_903995435.1 ">lcl|NC_067155.1_cds_XP_051018459.1_20262 [gene=Six5] [db_xref=GeneID:127203671] [protein=homeobox protein SIX5] [protein_id=XP_051018459.1] [location=join(13557655..13558430,13559216..13560018,13560133..13560722)] [gbkey=CDS]"
```
This plot shows that the rounding differences between ExtRamp 1.0 and 2.0 may be caused by the two minimums in close proximity within the first 8% of the sequence.

# CONTACT
Questions? Open a new issue on GitHub or email us at: mattcloward@byu.edu

Thank you, and happy researching!