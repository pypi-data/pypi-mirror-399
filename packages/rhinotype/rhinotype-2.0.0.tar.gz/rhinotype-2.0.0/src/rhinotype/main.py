import os
import sys
import subprocess
import argparse
from Bio import SeqIO
from Bio.Seq import Seq
import numpy as np
from Bio.Data.CodonTable import TranslationError
import matplotlib
matplotlib.use('Agg')
import time

# Tee class to duplicate stdout and stderr to a log file
class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# Get absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

try:
    from .getprototypeseqs import getprototypeseqs
    from .readfasta import read_fasta
    from .SNPeek import SNPeek
    from .assign_types import assign_types
    from .pairwise_distances import pairwise_distances
    from .overall_mean_distance import overall_mean_distance
    from .count_SNPs import count_snp
    from .plot_frequency import plot_frequency
    from .plot_distances import plot_distances
    from .plot_tree import plot_tree
    from .plot_AA import plot_AA
except ImportError as e:
    # Added the specific error 'e' for better debugging
    print(f"Error: Could not import package modules. {e}")
    print("This is likely a bug in the rhinotype package.")
    sys.exit(1)

def read_file_lines(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def combine_sequences(seq1_lines, seq2_lines):
    return seq1_lines + seq2_lines

def write_combined_sequences(combined_lines, output_path):
    with open(output_path, 'w') as output_file:
        output_file.writelines(combined_lines)

def format_sequence_line_breaks(sequence, line_length=50):
    return '\n'.join([sequence[i:i + line_length] for i in range(0, len(sequence), line_length)])

def step_get_prototypes(region):
    print("--- Step 1: Get Prototype Sequences ---")
    try:
        getprototypeseqs(region)
        return region
    except Exception as e:
        print(f"Error getting prototype sequences: {e}")
        return None

def step_load_data(region, fasta_file=None):
    print("\n--- Step 2: Load Sequence Data ---")
    fasta_data = None
    user_choice = "Y" if fasta_file else "N"

    if fasta_file:
        if not os.path.exists(fasta_file):
            print(f"Error: File not found at {fasta_file}")
            return None, None, None
        fasta_data = read_fasta(fasta_file)
        print(f"Successfully read user file: {fasta_file}")
        return fasta_data, fasta_file, "Y"
    else:
        print("Using default dataset...")
        base_data_path = os.path.join(os.path.dirname(__file__), 'data')
        if region == "Vp1":
            fasta_file = os.path.join(base_data_path, 'vp1_test.fasta')
        elif region == "Vp4/2":
            fasta_file = os.path.join(base_data_path, 'test.fasta')
        else:
            print(f"Error: Unknown region '{region}'. Cannot find default data.")
            return None, None, None
        if not os.path.exists(fasta_file):
            print(f"Error: Default file not found at {fasta_file}")
            return None, None, None
        fasta_data = read_fasta(fasta_file=fasta_file)
        print(f"Successfully read default file: {fasta_file}")
        return fasta_data, fasta_file, "N"

def step_run_snpeek(fasta_data, region):
    print("\n--- Step 3: Running SNPeek Analysis ---")
    SNPeek(fasta_data, region=region)
    print("SNPeek analysis complete.")

def step_run_alignment(fasta_file, user_choice_str, region, threads = 2):
    print("\n--- Step 4: Running Alignment ---")
    input_align = ""

    # Determine user's working directory and reference file path
    user_dir = os.getcwd() # Use current working directory for all outputs
    ref_file = os.path.join(user_dir, "RVRefs", "RVRefs.fasta")

    if user_choice_str.upper() == "Y":
        print("Combining user sequences with references...")

        # Note: The user_dir for the input fasta_file might be different
        # from the CWD, so we get its absolute directory.
        input_file_dir = os.path.dirname(os.path.abspath(fasta_file))

        if not os.path.exists(ref_file):
            print(f"Error: Reference file not found at {ref_file}")
            return None

        file1_path = fasta_file
        file2_path = ref_file

        seq1_lines = read_file_lines(file1_path)
        seq2_lines = read_file_lines(file2_path)
        combined_seq_lines = combine_sequences(seq1_lines, seq2_lines)

        output_file_path = os.path.join(user_dir, "combined_sequences.fasta")
        write_combined_sequences(combined_seq_lines, output_file_path)

        print(f"Combined sequences written to {output_file_path}")
        print("Running MAFFT alignment (this may take a moment)...")

        align_output_file = os.path.join(user_dir, "sequence_align.fasta")

        try:
            with open(align_output_file, "w") as out_file:
                subprocess.run(
                    ["mafft", "--auto", "--thread", str(threads), output_file_path],
                    stdout=out_file,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            print(f"Alignment written to {align_output_file}")
            input_align = align_output_file
        except FileNotFoundError:
            print("Error: 'mafft' command not found. Please ensure MAFFT is installed.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error during MAFFT execution: {e}")
            return None

    elif user_choice_str.upper() == "N":
        print("Using default alignment file...")
        base_data_path = os.path.join(os.path.dirname(__file__), 'data')
        if region == "Vp1":
            input_align = os.path.join(base_data_path, 'vp1_align.fasta')
        elif region == "Vp4/2":
            input_align = os.path.join(base_data_path, 'input_aln.fasta')

        if not os.path.exists(input_align):
            print(f"Error: Default alignment file not found at {input_align}")
            return None

    fasta_align = read_fasta(fasta_file=input_align)
    print(f"Successfully read alignment file: {input_align}")
    return fasta_align

def step_genotype_and_distance(fasta_align, region, user_seq_names, model, genotyping_threshold):
    """
    Calculates pairwise distances and assigns genotypes based on a
    USER-SUPPLIED threshold.
    """
    print("\n--- Step 5: Genotype and Distance Analysis ---")

    # 1. Calculate the full distance matrix ONCE.
    print("Calculating pairwise distance matrix...")
    try:
        # Note: We pass the model string (e.g., "k2p") directly
        # Changed gap_deletion to False to use Pairwise Deletion instead of Complete Deletion.
        # This is more robust for large datasets with potential gaps/missing data.
        distances = pairwise_distances(fasta_align, model, gap_deletion=False)
    except Exception as e:
        print(f"Error: Failed to calculate distance matrix. {e}")
        return None, None

    # 2. Validate and use the user-defined threshold.
    if genotyping_threshold is None or genotyping_threshold <= 0 or genotyping_threshold > 1.0:
        print(f"Error: Invalid threshold '{genotyping_threshold}'. Must be a positive value, <= 1.0.")
        return None, None

    print(f"Using user-defined p-distance threshold: {genotyping_threshold}")

    # 3. Pass the pre-calculated matrix and user's threshold to assign_types
    try:
        genotypes = assign_types(
            fasta_align,
            user_input=region, 
            model=model,
            threshold=genotyping_threshold,
            user_seq_names=user_seq_names,
            distances_matrix=distances
        )
    except Exception as e:
        print(f"Error: Failed during genotype assignment. {e}")
        return None, None

    # 4. Calculate overall mean
    overall_mean_distance(fasta_align, model=model, gap_deletion=True, distance_matrix=distances)

    print("\nGenotype distance analysis complete")
    return genotypes, distances

def step_run_snp_count(fasta_data):
    print("\n--- Step 6: SNP Counting ---")
    count_snp(fasta_data)
    print("\nCount SNP analysis complete")

def step_run_plotting(genotypes, distances, region):
    print("\n--- Step 7: Generating Plots ---")

    plot_frequency(genotypes, region)
    plot_distances(distances, region)

    # 1. Replace all Inf with NaN
    clean_distances = distances.replace([np.inf, -np.inf], np.nan)

    # 2. Find the *names* of sequences that have any NaN values
    # (axis=1 checks row-wise, .any() finds if *any* NaN exists)
    bad_seq_names = clean_distances.index[clean_distances.isna().any(axis=1)].tolist()

    if bad_seq_names:
        print(f"Warning: Removing {len(bad_seq_names)} sequences with non-finite distances from tree (e.g., all-gap sequences).")
        # 3. Drop these names from both the rows (index) and columns
        clean_distances = clean_distances.drop(index=bad_seq_names, columns=bad_seq_names)

    # 4. Check if the matrix is still valid for clustering
    if clean_distances.shape[0] < 2:
        print("Warning: Cannot generate tree. Less than 2 valid sequences after cleaning distances.")
    else:
        print(f"Plotting tree with {clean_distances.shape[0]} valid sequences.")
        plot_tree(clean_distances, region)

def step_run_aa_analysis(fasta_align_data, user_choice_str, region):
    print("\n--- Step 8: Amino Acid Analysis ---")

    if user_choice_str.upper() == "Y":
        # --- USER MODE ---
        # This code robustly translates aligned sequences,
        # handling gaps ('-') and ambiguities ('N').
        print("Translating aligned sequences")
        sequences_to_plot = []

        headers = fasta_align_data['headers']
        sequences = fasta_align_data['sequences']

        # Cache for codon translation to avoid repeated Bio.Seq overhead
        # Pre-populate with common gap cases
        codon_cache = {
            '---': '-',
            '...': '-',
            '~~~': '-'
        }

        def translate_codon_cached(c):
            if c in codon_cache:
                return codon_cache[c]

            # If gap exists but not full (e.g. 'A--'), treat as gap per original logic
            if '-' in c:
                codon_cache[c] = '-'
                return '-'

            try:
                # Use Biopython to translate
                aa = str(Seq(c).translate())
                codon_cache[c] = aa
                return aa
            except TranslationError:
                codon_cache[c] = 'X'
                return 'X'
            except Exception:
                # Handle partial codons at end or weird chars
                codon_cache[c] = 'X'
                return 'X'

        for i in range(len(headers)):
            header = headers[i]
            nuc_sequence_str = sequences[i]

            # Slice into codons efficiently
            # This is much faster than loop + slice
            codons = [nuc_sequence_str[j:j+3] for j in range(0, len(nuc_sequence_str), 3)]

            # Remove last chunk if partial
            if len(codons) > 0 and len(codons[-1]) < 3:
                codons.pop()

            # Map using cache
            # This turns O(N*L) Biopython calls into O(1) lookups
            protein_sequence = [translate_codon_cached(c) for c in codons]

            # Join the list of amino acids into a single string
            translated_sequence_str = "".join(protein_sequence)

            # Format for plot_AA
            formatted_sequence = f">{header}\n{format_sequence_line_breaks(str(translated_sequence_str))}"
            sequences_to_plot.append(formatted_sequence)

        all_sequences_str = '\n'.join(sequences_to_plot)
        plot_AA(all_sequences_str, region)

    else:
        # --- DEMO MODE ---
        print("Using pre-translated file for 'demo' mode...")
        base_data_path = os.path.join(os.path.dirname(__file__), "data")
        translated_file = ""
        if region == "Vp1":
            translated_file = os.path.join(base_data_path, "vp1_test_translated.fasta")
        elif region == "Vp4/2":
            translated_file = os.path.join(base_data_path, "test.translated.fasta")

        if translated_file and os.path.exists(translated_file):
            plot_AA(translated_file, region)
        else:
            print(f"Warning: Could not find demo translated file at {translated_file}")

def run_pipeline(region=None, fasta_file=None, model="p-distance", genotyping_threshold=None, threads=2):
    print(f"\n=== RHINOTYPE PIPELINE ===")
    print(f"Using genetic distance model: {model}") 

    region = step_get_prototypes(region)
    if not region:
        return
    fasta_data, fasta_file, user_choice = step_load_data(region, fasta_file)
    if fasta_data is None:
        return

    user_seq_names = None
    if user_choice.upper() == "Y":
        user_seq_names = [h.lstrip('>') for h in fasta_data['headers']]
        print(f"Loaded {len(user_seq_names)} user sequence headers for filtering.")
    else:
        print("Running in 'demo' mode. Will classify all non-prototypes in the alignment.")

    step_run_snpeek(fasta_data, region)
    fasta_align = step_run_alignment(fasta_file, user_choice, region, threads)
    if fasta_align is None:
        print("Alignment failed. Exiting.")
        return

    # Pass the threshold from the command line down to this function
    genotypes, distances = step_genotype_and_distance(
        fasta_align, 
        region, 
        user_seq_names, 
        model, 
        genotyping_threshold
    )

    if genotypes is None or distances is None:
        print("Genotype and distance analysis failed. Exiting.")
        return

    step_run_snp_count(fasta_data)
    step_run_plotting(genotypes, distances, region)

    step_run_aa_analysis(fasta_align, user_choice, region)

    print(f"\nPipeline complete.")

def main():
    parser = argparse.ArgumentParser(
        prog="rhinotype",
        description=(
            "Rhinotype — a CLI tool for assigning rhinovirus genotypes "
            "based on VP1 or VP4/2 genomic regions."
        ),
        usage="%(prog)s --input FILE --region {Vp1,Vp4/2} --threshold {VALUE} [--model MODEL] [--threads {VALUE}]",
        epilog=(
            "Examples:\n"
            "  rhinotype --input my_sequences.fasta --region Vp1 --model p-distance --threshold 0.105 --threads 2\n"
            "  rhinotype --input my_sequences.fasta --region Vp4/2 --model k2p --threshold 0.405\n"
            "\n"
            "Models supported: p-distance, jc69, k2p, tn93"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--input", type=str, required=True,
                    help="Path to user FASTA file")
    parser.add_argument("--region", type=lambda s: s.strip().capitalize(),
                    choices=["Vp1", "Vp4/2"], required=True,
                    help="Genomic region (e.g., Vp1 or Vp4/2)")
    parser.add_argument("--model", 
                    choices=["p-distance", "jc69", "k2p", "tn93"],
                    default="p-distance", 
                    help="Evolutionary model to use (default: p-distance). Options: p-distance, jc69, k2p, tn93")
    parser.add_argument("-t", "--threshold", 
                        type=float, 
                        required=False,
                        default=None,
                        help="The p-distance threshold for genotyping (e.g., 0.105). Default: 0.105 if not specified.")
    parser.add_argument("--threads", "-T",
                        type=int, default=2,
                        help="Select the number of threads mafft to use for alignment")

    args = parser.parse_args()

    # --- Set Smart Defaults ---
    if args.threshold is None:
        # Standard default for Rhinovirus genotyping (McIntyre et al.)
        args.threshold = 0.105
        print(f"No threshold provided. Using default threshold: {args.threshold}")

    # --- Create reports directory and log file ---
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(logs_dir, f"rhinotype_log_{timestamp}.txt")

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        with open(log_file_path, "w") as log_file:
            # Tee stdout and stderr to the log file
            sys.stdout = Tee(original_stdout, log_file)
            sys.stderr = Tee(original_stderr, log_file)

            run_pipeline(
                region=args.region, 
                fasta_file=args.input, 
                model=args.model,
                genotyping_threshold=args.threshold,
                threads=args.threads
            )
    finally:
        # --- Restore stdout and stderr ---
        sys.stdout = original_stdout
        sys.stderr = original_stderr

if __name__ == "__main__":
    main()
