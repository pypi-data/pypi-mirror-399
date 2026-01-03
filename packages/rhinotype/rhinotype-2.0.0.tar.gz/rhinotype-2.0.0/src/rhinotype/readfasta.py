from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# Function 1
def compare_lengths(seqs):
    # Calculate the maximum length from the list of sequences
    max_length = max(len(seq) for seq in seqs)

    # Adjust each sequence to have the same length as the longest sequence
    # Use ljust for efficient padding
    adjusted_seqs = [seq.ljust(max_length, '-') for seq in seqs]

    return adjusted_seqs

# Function 2
def read_fasta(fasta_file):
    # Read the DNA sequences from a FASTA file
    alignment = list(SeqIO.parse(fasta_file, "fasta"))

    # Extract the sequences and headers
    seq_list = [str(record.seq) for record in alignment]
    header_list = [record.id for record in alignment]

    # Adjust all sequences to the length of the longest sequence
    seq_list = compare_lengths(seq_list)

    # Return a dictionary containing the sequences and their corresponding headers
    return {'sequences': seq_list, 'headers': header_list}

if __name__ == "__main__":
    compare_lengths()
    read_fasta()
