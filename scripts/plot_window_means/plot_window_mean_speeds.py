# This script plots the window mean speeds for a given species and sequence, assuming
# the get_window_mean_speeds.sh script has already been run for the species.

import sys
import re
from scipy.stats import zscore
import matplotlib.pyplot as plt
import numpy as np

def getGeneNameFromHeader(header):
    geneMatch = re.search(r'gene=\'?([^\]]+)\'?\]', header)
    if geneMatch:
        gene = geneMatch.group(1).upper()
        return gene
    return None

def getWindowMeans(inPath, header):
    with open(inPath) as inf:
        currentHeader = inf.readline().strip()
        windowMeans = inf.readline().strip()
        while currentHeader:
            if header in currentHeader:
                windowMeans = windowMeans.split(",")
                windowMeans = np.array([float(x) for x in windowMeans])
                return windowMeans
            currentHeader = inf.readline().strip()
            windowMeans = inf.readline().strip()
    return None

def getRampLength(windowMeans):
    # the ramp length is 0 to the first window mean that greater than the mean of the window means
    mean = sum(windowMeans) / len(windowMeans)
    for i, windowMean in enumerate(windowMeans):
        if windowMean > mean:
            return i

def hasRamp(windowMeans, percentThatIsRamp=8.0, ribosomeWindowLength=9):
    bestMean = min(windowMeans)
    pos = np.where(windowMeans == bestMean)[0][0] # gets the first minimum
    perc = float(100*(pos/float(len(windowMeans)))) # percentages x 100
    if perc <= percentThatIsRamp:
            # Note: this doesn't account for the rare case where the ramp ends at the end of the sequence
            return True
    return False

def getLastRampWindowIndex(pos, windowMeans, mean):
    """
    Gets the index of the last efficiency window of the ramp, which is the index of the first value
    after the ramp starts that is greater than the sequence's mean efficiency. If no such index exists,
    the ramp does not exist and -1 is returned.
    """
    indicesGreaterThanMean = np.where(windowMeans[pos:] >= mean) + pos
    return indicesGreaterThanMean[0][0] if len(indicesGreaterThanMean[0]) > 0 else -1


if __name__ == "__main__":
    speciesID = sys.argv[1]
    header = sys.argv[2]
    geneName = getGeneNameFromHeader(header)

    inPath = f"../../outputs/plot_window_means/{speciesID}-hmean-2.0-windowmeans.fa"
    figPath = f"../../outputs/plot_window_means/windowMeans-{speciesID}-{geneName}.png"

    windowMeans = getWindowMeans(inPath, header)

    doesHaveRamp = hasRamp(windowMeans)
    # for plotting the ramp region cutoff line
    eightPercentIndex = int(len(windowMeans) * 0.08)
    # for calculating minimum ramp and non-ramp efficiencies
    rampLength = getRampLength(windowMeans) if doesHaveRamp else eightPercentIndex

    min_ramp_efficiency = min(windowMeans[:rampLength])
    min_nonramp_efficiency = min(windowMeans[rampLength:])

    # graph the window means
    plt.figure(figsize=(6,4))
    plt.ylim(0, 1.1)
    plt.plot(windowMeans, color='#777777', linewidth=2)
    # plot eight percent vertical line
    plt.vlines(eightPercentIndex-1, 0, 1.1, colors='#000000', linestyles='dashed', label='Ramp Region Cutoff')
    # plot minimums as horizontal lines
    plt.hlines(min_ramp_efficiency, 0, len(windowMeans)-1, colors='#E69F00', linestyles='dashed', label='Min Ramp Efficiency')
    plt.hlines(min_nonramp_efficiency, 0, len(windowMeans)-1, colors='#56B4E9', linestyles='dashed', label='Min Non-Ramp Efficiency')
    # plot orange for the window means that are in the ramp
    if doesHaveRamp:
        plt.plot(range(rampLength), windowMeans[:rampLength], color='#E69F00', linewidth=2)
    plt.xlabel("9-Codon Sliding Window")
    plt.ylabel("Harmonic Mean Codon Efficiency")
    plt.title(f"Ribosome Translation Efficiency in {geneName}")
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(figPath, dpi=350)

    print("done.")