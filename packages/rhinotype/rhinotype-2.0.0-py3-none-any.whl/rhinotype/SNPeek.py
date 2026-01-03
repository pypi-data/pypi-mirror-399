import os
import pandas as pd
from Bio import SeqIO
import matplotlib.pyplot as plt
import numpy as np

# --- FASTA Reading Function ---
def read_fasta(fasta_file):
    sequences = []
    headers = []
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences.append(str(record.seq))
        headers.append(record.id)
    return {"sequences": sequences, "headers": headers}

# --- Sequence Comparison Function ---
def compare_sequences(seqA, seqB):
    differences = [i for i in range(len(seqA)) if seqA[i] != seqB[i]]
    subsType = [seqB[i] for i in differences]
    return pd.DataFrame({"position": differences, "subsType": subsType})

# --- SNPeek Plotting Function ---
def SNPeek(fastaData, region="Unknown", output_dir=None, showLegend=False):
    sequences = fastaData["sequences"]
    seqNames = fastaData["headers"]
    genomeLength = max([len(seq) for seq in sequences])

    # Define color map for nucleotide substitutions
    colorMap = {"A": "green", "T": "red", "C": "blue", "G": "yellow"}

    diffList = []
    for i in range(1, len(sequences)):
        diff = compare_sequences(sequences[0], sequences[i])
        diff["color"] = diff["subsType"].map(colorMap).fillna("black")
        diffList.append(diff)

    # Dynamic figure height
    num_sequences = len(sequences)
    fig_height = max(10, num_sequences * 0.25)

    plt.figure(figsize=(15, fig_height), dpi = 600)
    plt.xlim(1, genomeLength)
    plt.ylim(0.5, num_sequences - 0.5)
    plt.xlabel(f"Genome Position (reference: {seqNames[0]})", fontsize=10)
    
    # y-ticks: 1 to N-1. Labels: seqNames[1:]
    plt.yticks(ticks=np.arange(1, num_sequences), labels=seqNames[1:], fontsize=10)
    
    plt.gca().yaxis.set_tick_params(labelsize=8)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    for i, diff in enumerate(diffList, start=1):
        for _, row in diff.iterrows():
            plt.plot([row["position"], row["position"]], [i - 0.4, i + 0.4], color=row["color"], marker="|")

    if showLegend:
        plt.legend(["A", "T", "C", "G", "Other"],
                   handlelength=0.8, markerfirst=False,
                   loc="upper left", bbox_to_anchor=(1, 1),
                   facecolor="white", framealpha=0.7)

    plt.title(f"{region} Nucleotide Differences from Reference Sequence")

    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "SNPeek.png")
    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")
