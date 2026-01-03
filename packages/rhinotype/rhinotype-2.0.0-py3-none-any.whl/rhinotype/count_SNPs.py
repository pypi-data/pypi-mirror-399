from .genetic_distances import count_snps_helper

def count_snp(fasta_data, gap_deletion=True):
    # run countSNP function
    snps = count_snps_helper(fasta_data, gap_deletion=gap_deletion)
    # output
    return snps

if __name__ == "__main__":
    count_snp()
