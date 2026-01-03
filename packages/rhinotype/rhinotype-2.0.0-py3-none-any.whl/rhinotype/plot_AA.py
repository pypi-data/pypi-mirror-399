import pandas as pd
import matplotlib.pyplot as plt
import os
from io import StringIO

def read_AA(AAfastaFile):
    # Check if the input is a file path or a string containing the FASTA data
    if isinstance(AAfastaFile, str) and AAfastaFile.startswith(">"):  # it's a string containing FASTA data
        # Use StringIO to simulate a file object
        fasta_file = StringIO(AAfastaFile)
    else:  # it's a file path
        fasta_file = open(AAfastaFile, 'r')

    lines = fasta_file.readlines()
    seqList = []
    headerList = []
    currentSeq = []

    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            if currentSeq:
                seqList.append(''.join(currentSeq))
            currentSeq = []
            headerList.append(line[1:])
        else:
            currentSeq.append(line.upper())

    if currentSeq:
        seqList.append(''.join(currentSeq))

    # Close the StringIO or the file
    if isinstance(fasta_file, StringIO):
        fasta_file.close()
    else:
        fasta_file.close()

    return {'sequences': seqList, 'headers': headerList}

def plot_AA(AAfastaFile, region, output_dir=None, showLegend=False):
    # If a string of sequences is passed, process it directly
    fastaData = read_AA(AAfastaFile)
    sequences = fastaData['sequences']
    seqNames = fastaData['headers']
    proteinLength = max(len(seq) for seq in sequences)

    def compareSequences(seqA, seqB):
        differences = [i for i in range(len(seqA)) if seqA[i] != seqB[i]]
        subsType = [seqB[i] for i in differences]
        return pd.DataFrame({'position': differences, 'subsType': subsType})

    colorMap = {
        'R': 'red', 'H': 'red', 'K': 'red',
        'D': 'blue', 'E': 'blue',
        'S': 'green', 'T': 'green', 'N': 'green', 'Q': 'green',
        'A': 'yellow', 'V': 'yellow', 'I': 'yellow', 'L': 'yellow', 'M': 'yellow', 
        'F': 'yellow', 'W': 'yellow', 'P': 'yellow', 'G': 'yellow', 'Y': 'yellow', 'C': 'yellow'
    }

    diffList = []
    for i in range(1, len(sequences)):
        diff = compareSequences(sequences[0], sequences[i])
        diff['color'] = diff['subsType'].map(colorMap).fillna('gray')
        diffList.append(diff)

    # Dynamic figure height
    num_sequences = len(sequences)
    fig_height = max(6, num_sequences * 0.25)
    
    plt.figure(figsize=(15, fig_height), dpi = 600)
    plt.xlim(1, proteinLength)
    # y-axis limits: 0.5 to N-0.5 (for N-1 rows)
    plt.ylim(0.5, num_sequences - 0.5) 
    plt.xlabel(f"Protein Position of {seqNames[0]}, acting as reference")
    
    # y-ticks: 1 to N-1. Labels: seqNames[1:]
    plt.yticks(range(1, num_sequences), seqNames[1:], rotation=0, fontsize=8)

    for i, diff in enumerate(diffList):
        # i goes from 0 to N-2. Plot at y = i + 1.
        for j in range(len(diff)):
            plt.plot([diff['position'].iloc[j], diff['position'].iloc[j]], 
                     [i + 1 - 0.4, i + 1 + 0.4], color=diff['color'].iloc[j])

    if showLegend:
        plt.legend(["+ve charged", "-ve charged", "Polar", "Non-polar", "Other"],
                   loc='upper left', bbox_to_anchor=(1, 1), framealpha=0.7)
    plt.title(f"{region} Amino Acid Differences from Reference Sequence")

    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "AA.png")

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    read_AA()
    plot_AA()
