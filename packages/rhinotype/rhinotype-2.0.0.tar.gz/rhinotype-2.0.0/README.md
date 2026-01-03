# rhinotype
rhinotype: A Python Package for the Classification of Rhinoviruses

## Table of contents

1. [Background](#background)
2. [Workflow](#workflow)
3. [Installation](#installation)
4. [getprototypeseqs](#getprototypeseqs)
5. [readfasta](#readfasta)
6. [SNPeek](#snpeek)
7. [assign_types](#assign_types)
8. [pairwise_distances](#pairwise_distances)
9. [overall_mean_distance](#overall_mean_distance)
10. [count_SNPs](#count_snps)
11. [plot_frequency](#plot_frequency)
12. [plot_distances](#plot_distances)
13. [plot_tree](#plot_tree)
14. [plot_AA](#plot_aa)
15. [Citation](#citation)
16. [Contributors](#contributors)

## <a id="background"></a>Background 

Among the major causes of human respiratory infections, rhinovirus causes around 50% of all the year-round cases of common cold. This virus belongs to the Enterovirus genus in the Picornaviridae family. RV-A, RV-B, and RV-C are the three species under the genus Rhinovirus, each having about 169 different genotypes. Rhinoviruses are positive-sense, non-enveloped RNA viruses with approximately 7.2 kilobases long genome. The genome codes for seven non-structural proteins and four structural proteins—VP1, VP2, VP3, and VP4—which are part of the genome encoding viral replication and host infection mechanisms. Genotyping of Rhinovirus, until now, is done manually, while an R software package, [rhinotypeR](https://github.com/omicscodeathon/rhinotypeR/tree/main), allows for fully automated genotyping based on the VP4 region. The Python rhinovirus type package brings out VP1 and VP4 regions that aim to improve acuity in genotyping. The VP1 region has been tested to display better acuity in genotypic identification, while the VP4/2 region ensures compatibility under one universal amplification protocol for rapid genotyping.

## <a id="workflow"></a>Workflow

![Workflow](figures/rhinotype%20workflow.svg)

## <a id="installation"></a>Installation

You can install the package using the following command:

```
pip install rhinotype
```

**Note:** This package requires [MAFFT](https://mafft.cbrc.jp/alignment/software/) for sequence alignment. Please ensure that you have MAFFT installed and that it is available in your system's PATH.

#### Run the package

```
rhinotype --mode {demo,user} --region {Vp1,Vp4/2} --threshold {VALUE} [--input FILE] [--model MODEL] --threads {VALUE}
```

## <a id="getprototypeseqs"></a>getprotypeseqs

Gets the prototype sequences of the Rhinovirus genotypes and save the reference fasta file into RVRefs directory. Making both VP1 and VP4/2 sequences available depending on whch region you have. The tool then combines user sequences together with the prototype sequences and align them using MAFFT or any other alignment tool.

## <a id="readfasta"></a>readfasta

Reads the alignments/sequences. Compares the input sequences and pads the short sequences with - until they are long as the longest sequence. The sequences are then stored in a dictionary with the sequence name as the key and the sequence as the value.

## <a id="snpeek"></a>SNPeek

SNPeek function visualizes single nuclotide polymorphisms(SNPs) using the users sequences, relative to a specified reference sequence. To specify a reference sequence, the user should move the sequence to the bottom of the alignment. Substitutions are color coded by nucleotide: A = green, T = red, C = blue, G = yellow.

## <a id="assign_types"></a>assign_types

The ```assign_types``` function assigns genotype to the sequences in the fasta file by comparing them to the prototype sequences. The classification is based on pairwise distances calculated using a specified distance model. Users can adjust parameters for gap deletion and threshold to control the classification process. The function reads prototype sequences from predefined CSV files based on the specified prototype type.

Parameters:

- ```fasta_data``` (DataFrame): A DataFrame containing the sequences to be classified.
- ```model``` (str): The distance model to use (default is 'p-distance').
- ```gap_deletion``` (bool): Whether to apply gap deletion in distance calculations (default is True).
- ```threshold``` (float): The distance threshold for classification (default is 0.105)

## <a id="pairwise_distances"></a>pairwise_distances

Calculates pairwise genetic distances between sequences in a FASTA dataset using the specified distance model. The function supports various models for distance calculation and can optionally apply gap deletion. The result is a DataFrame showing the distances between each pair of sequences.

Parameters:

- ```fasta_data``` (DataFrame): A DataFrame containing the sequences to be analyzed.
- ```model``` (str): The distance model to use. Options include:
    - ```"p-distance"```: Simple proportion of differing sites.
    - ```"JC"```: Jukes-Cantor model.
    - ```"Kimura2p"```: Kimura 2-parameter model.
    - ```"Tamura3p"```: Tamura 3-parameter model.
- ```gap_deletion``` (bool): Whether to apply gap deletion in the distance calculation (default is True).
- ```Output```: The function returns a numpy array containing the pairwise distances between the sequences

## <a id="overall_mean_distance"></a>overall_mean_distance

Calculates the overall mean genetic distance between sequences using various distance models. The function supports multiple models and can optionally handle gap deletion in sequences. It provides an average distance value based on the chosen model.

## <a id="count_snps"></a>count_SNPs

Counts the single nucleotide polymorphisms (SNPs) in the provided sequence data and can optionally handle gap deletion in the sequences.

## <a id="plot_frequency"></a>plot_frequency

Generates a bar chart visualizing the frequency of assigned types from a DataFrame. The function creates a bar chart where each bar represents the count of a specific type, and colors are used to differentiate between species. The chart is saved as an image file and can optionally include a legend.

## <a id="plot_distances"></a>plot_distances

Generates a heatmap to visualize the pairwise genetic distances between sequences and saves the plot as an image file. The color scale represents the magnitude of genetic distances.

## <a id="plot_tree"></a>plot_tree

Generates a hierarchical clustering dendrogram from the pairwise genetic distances between sequences. The function performs complete linkage clustering and visualizes the results as a tree diagram. The dendrogram is saved as an image file.

## <a id="plot_aa"></a>plot_AA

Visualizes amino acid differences between protein sequences. The function compares each sequence to a reference sequence and plots the differences as colored bars, categorizing amino acids based on their properties. The plot is saved as an image file.

## <a id="citation"></a>Citation

## <a id="contributors"></a>Contributors

1. [Ephantus Wambui](https://github.com/Ephantus-Wambui)

2. [Daniel Okoro](https://github.com/danny6200)

3. [Andrew Acheampong](https://github.com/AcheampongAndy)

4. [Parcelli Jepchirchir](https://github.com/Parcelli)

5. [Olaitan I. Awe](https://github.com/laitanawe)
