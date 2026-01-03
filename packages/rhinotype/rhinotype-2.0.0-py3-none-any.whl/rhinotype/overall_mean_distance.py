import numpy as np
import pandas as pd
from .genetic_distances import (
    calc_p_distance,
    calc_jukes_cantor_distance,
    calc_kimura_2p_distance,
    calc_tamura_nei_distance
)

def _calculate_mean_from_matrix(dist_matrix):
    """
    Helper to calculate the mean of the upper triangle of a distance matrix.
    Handles pandas DataFrame or numpy array.
    """
    if isinstance(dist_matrix, pd.DataFrame):
        data = dist_matrix.values
    else:
        data = dist_matrix

    n = data.shape[0]
    if n < 2:
        return np.nan

    # Get upper triangle indices (excluding diagonal)
    triu_indices = np.triu_indices(n, k=1)
    distances = data[triu_indices]

    # Filter valid distances (not NaN and not Inf)
    valid_mask = np.isfinite(distances)
    valid_distances = distances[valid_mask]

    if len(valid_distances) == 0:
        return np.nan

    return np.mean(valid_distances)

def overall_mean_distance(fasta_data, model='p-distance', gap_deletion=True, distance_matrix=None):
    """
    Calculates the overall mean genetic distance of the dataset.

    If 'distance_matrix' is provided (DataFrame or numpy array), it uses that 
    instead of re-calculating.
    """

    if distance_matrix is not None:
        result = _calculate_mean_from_matrix(distance_matrix)
        print(f"Overall mean genetic distance ({model}): {result:.4f}")
        return result

    # If no matrix provided, calculate it using the vectorized functions
    # (These are now fast thanks to the optimization in genetic_distances.py)

    calc_func = None
    if model == "p-distance":
        calc_func = calc_p_distance
    elif model == "jc69":
        calc_func = calc_jukes_cantor_distance
    elif model == "k2p":
        calc_func = calc_kimura_2p_distance
    elif model == "tn93":
        calc_func = calc_tamura_nei_distance
    else:
        raise ValueError(f"Unknown model specified: '{model}'. "
                         "Choose from 'p-distance', 'jc69', 'k2p', or 'tn93'")

    print(f"Calculating distance matrix for overall mean ({model})...")
    dist_matrix = calc_func(fasta_data, gap_deletion=gap_deletion)

    result = _calculate_mean_from_matrix(dist_matrix)
    print(f"Overall mean genetic distance ({model}): {result:.4f}")
    return result

if __name__ == "__main__":
    print("This module provides the overall_mean_distance() function.")
