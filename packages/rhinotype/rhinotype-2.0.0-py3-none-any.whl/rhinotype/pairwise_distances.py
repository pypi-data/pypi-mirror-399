import pandas as pd
from .readfasta import read_fasta
from .genetic_distances import ( calc_p_distance, calc_jukes_cantor_distance, calc_kimura_2p_distance, calc_tamura_nei_distance )

def pairwise_distances(fasta_data, model='p-distance', gap_deletion=True):
    """
    Acts as a switchboard to calculate a distance matrix using the
    specified evolutionary model.

    Args:
        fasta_data (dict): A dictionary from read_fasta {'headers': [...], 'sequences': [...]}.
        model (str): The distance model to use.
                     Options: 'p-distance', 'jc69', 'k2p', 'tn93'.
        gap_deletion (bool): Whether to use complete deletion (True) or 
                             let the model handle it (False for k2p/tn93).

    Returns:
        pd.DataFrame: A square DataFrame containing the pairwise distances.
    """
    model_name = model.lower()

    print(f"Calculating distance matrix using model: {model_name} (gap_deletion={gap_deletion})")

    if model_name == 'p-distance':
        # p-distance uses complete deletion by default if gap_deletion=True
        return calc_p_distance(fasta_data, gap_deletion=gap_deletion)

    elif model_name == 'jc69':
        # JC69 is based on p-distance, so it also uses complete deletion
        return calc_jukes_cantor_distance(fasta_data, gap_deletion=gap_deletion)

    elif model_name == 'k2p':
        # K2P (Kimura 2-Parameter)
        # We pass gap_deletion here. If True, it performs complete deletion first.
        # If False, the helper function will perform pairwise deletion.
        return calc_kimura_2p_distance(fasta_data, gap_deletion=gap_deletion)

    elif model_name == 'tn93':
        # TN93 (Tamura-Nei 93)
        # Same as K2P, it respects the gap_deletion flag.
        return calc_tamura_nei_distance(fasta_data, gap_deletion=gap_deletion)

    else:
        raise ValueError(f"Unknown distance model: '{model}'. "
                         "Valid models are: 'p-distance', 'jc69', 'k2p', 'tn93'.")

if __name__ == "__main__":
    print("This module provides the main pairwise_distances() function.")
    pairwise_distances()
