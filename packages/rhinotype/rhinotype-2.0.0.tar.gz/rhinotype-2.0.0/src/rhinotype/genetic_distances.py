import numpy as np
import pandas as pd
import math

def _seqs_to_int_array(seqs):
    """
    Convert a list of sequence strings to a numpy integer array.
    Mapping: A->0, G->1, C->2, T->3, Other->4
    """
    if not seqs:
        return np.empty((0, 0), dtype=np.int8)

    # Convert to character array
    # Assume all seqs have same length (guaranteed by readfasta)
    char_arr = np.array([list(s) for s in seqs], dtype='S1')

    # Create mapping table (ASCII to int)
    table = np.full(256, 4, dtype=np.int8)
    for base, val in zip([b'A', b'G', b'C', b'T', b'a', b'g', b'c', b't'], 
                         [0, 1, 2, 3, 0, 1, 2, 3]):
        table[ord(base)] = val

    return table[char_arr.view(np.uint8)]

def delete_missing_data_sites(seqs):
    """
    Removes columns (sites) that contain any gap or missing data ('-') 
    from a list of sequences.
    """
    if not seqs:
        return []

    seq_matrix = np.array([list(seq) for seq in seqs])
    # Assuming '-' is the gap character. 
    # Logic: Keep columns where NO element is '-'
    valid_columns = np.all(seq_matrix != '-', axis=0)

    cleaned_matrix = seq_matrix[:, valid_columns]

    # Return as list of strings
    return [''.join(row) for row in cleaned_matrix]

def _calculate_metrics_vectorized(seq_array, metric_type='p-dist', batch_size=100):
    """
    Core function to calculate pairwise metrics (SNPs, Transitions, Transversions)
    using vectorized operations with batching to save memory.

    seq_array: (N, L) int8 array (0=A, 1=G, 2=C, 3=T, 4=Other)

    Returns matrices based on metric_type.
    """
    N, L = seq_array.shape
    
    # Initialize result matrices
    if metric_type == 'p-dist':
        snp_matrix = np.full((N, N), np.nan)
        len_matrix = np.zeros((N, N))
    elif metric_type == 'k2p':
        ts_matrix = np.zeros((N, N)) # Transitions
        tv_matrix = np.zeros((N, N)) # Transversions
        len_matrix = np.zeros((N, N))
    elif metric_type == 'tn93':
        p1_matrix = np.zeros((N, N)) # Purine transitions (A<->G)
        p2_matrix = np.zeros((N, N)) # Pyrimidine transitions (C<->T)
        tv_matrix = np.zeros((N, N)) # Transversions
        len_matrix = np.zeros((N, N))

    # Process in batches of rows
    for i in range(0, N, batch_size):
        end_i = min(i + batch_size, N)
        batch_seqs = seq_array[i:end_i] # (B, L)

        # Broadcasting: (B, 1, L) vs (1, N, L) -> (B, N, L)
        # To avoid massive memory (B*N*L), we can iterate over N in blocks too if needed.
        # But (50 * 1000 * 1000) bytes is ~50MB, which is fine.

        # Valid pairs mask: neither is 4 (Gap/Other)
        # shape: (B, N, L)
        valid_mask = (batch_seqs[:, None, :] < 4) & (seq_array[None, :, :] < 4)

        # Count valid length
        valid_counts = valid_mask.sum(axis=2)
        len_matrix[i:end_i, :] = valid_counts

        # Difference mask where valid
        diff_mask = valid_mask & (batch_seqs[:, None, :] != seq_array[None, :, :])

        if metric_type == 'p-dist':
            snps = diff_mask.sum(axis=2)
            snp_matrix[i:end_i, :] = snps

        elif metric_type == 'k2p':
            # 0=A, 1=G (Purines -> //2 = 0)
            # 2=C, 3=T (Pyrimidines -> //2 = 1)
            type1 = batch_seqs[:, None, :] // 2
            type2 = seq_array[None, :, :] // 2

            # Transition: Same type (Purine-Purine or Pyr-Pyr) AND different base
            # Transversion: Different type AND different base (already implied by diff type)

            is_transition = diff_mask & (type1 == type2)
            is_transversion = diff_mask & (type1 != type2)
            ts_matrix[i:end_i, :] = is_transition.sum(axis=2)
            tv_matrix[i:end_i, :] = is_transversion.sum(axis=2)

        elif metric_type == 'tn93':
             # 0=A, 1=G, 2=C, 3=T
            b1 = batch_seqs[:, None, :]
            b2 = seq_array[None, :, :]

            # P1: Purine transition (A<->G) -> (0<->1)
            # P2: Pyrimidine transition (C<->T) -> (2<->3)
            # TV: Transversion

            is_p1 = diff_mask & ((b1 < 2) & (b2 < 2)) # Both < 2 means 0 or 1
            is_p2 = diff_mask & ((b1 >= 2) & (b2 >= 2)) # Both >= 2 means 2 or 3
            is_tv = diff_mask & ((b1 < 2) != (b2 < 2)) # One Purine, one Pyr

            p1_matrix[i:end_i, :] = is_p1.sum(axis=2)
            p2_matrix[i:end_i, :] = is_p2.sum(axis=2)
            tv_matrix[i:end_i, :] = is_tv.sum(axis=2)

    if metric_type == 'p-dist':
        return snp_matrix, len_matrix
    elif metric_type == 'k2p':
        return ts_matrix, tv_matrix, len_matrix
    elif metric_type == 'tn93':
        return p1_matrix, p2_matrix, tv_matrix, len_matrix

def count_snps_helper(fasta_data, gap_deletion=True):
    refs = fasta_data['sequences']
    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    seq_array = _seqs_to_int_array(refs)
    snps, lengths = _calculate_metrics_vectorized(seq_array, metric_type='p-dist')

    snps[lengths == 0] = np.nan
    return snps

def calc_p_distance(fasta_data, gap_deletion=True):
    refs = fasta_data['sequences']
    headers = fasta_data['headers']

    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    seq_array = _seqs_to_int_array(refs)
    snps, lengths = _calculate_metrics_vectorized(seq_array, metric_type='p-dist')

    with np.errstate(divide='ignore', invalid='ignore'):
        p_dist = snps / lengths

    # Handle lengths == 0
    p_dist[lengths == 0] = np.nan

    return pd.DataFrame(p_dist, index=headers, columns=headers)

def calc_jukes_cantor_distance(fasta_data, gap_deletion=True):
    # Relies on p-distance
    p_dist_df = calc_p_distance(fasta_data, gap_deletion=gap_deletion)
    p_dist = p_dist_df.values

    # JC69 formula
    # -3/4 * ln(1 - 4/3 * p)
    # boundary: p >= 0.75 -> inf

    jc_dist = np.zeros_like(p_dist)

    mask_inf = p_dist >= 0.749999
    mask_valid = ~mask_inf & ~np.isnan(p_dist)

    jc_dist[mask_inf] = np.inf
    jc_dist[np.isnan(p_dist)] = np.nan

    # Only calculate for valid
    arg = 1 - 1.3333333333333333 * p_dist[mask_valid]
    # Safety clip
    arg[arg <= 0] = 1e-9 

    jc_dist[mask_valid] = -0.75 * np.log(arg)

    return pd.DataFrame(jc_dist, index=p_dist_df.index, columns=p_dist_df.columns)

def calc_kimura_2p_distance(fasta_data, gap_deletion=True):
    refs = fasta_data['sequences']
    headers = fasta_data['headers']

    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    seq_array = _seqs_to_int_array(refs)
    ts, tv, length = _calculate_metrics_vectorized(seq_array, metric_type='k2p')

    # P = S / L, Q = V / L
    with np.errstate(divide='ignore', invalid='ignore'):
        P = ts / length
        Q = tv / length

    # arg1 = 1 - 2P - Q
    # arg2 = 1 - 2Q
    arg1 = 1 - 2*P - Q
    arg2 = 1 - 2*Q

    dist = np.full_like(length, np.nan)

    # Valid mask
    valid_mask = (length > 0) & (arg1 > 1e-9) & (arg2 > 1e-9)

    dist[valid_mask] = -0.5 * np.log(arg1[valid_mask]) - 0.25 * np.log(arg2[valid_mask])

    # Set Inf where mathematically impossible (and L > 0)
    inf_mask = (length > 0) & ((arg1 <= 1e-9) | (arg2 <= 1e-9))
    dist[inf_mask] = np.inf

    # Diagonal is 0
    np.fill_diagonal(dist, 0.0)

    return pd.DataFrame(dist, index=headers, columns=headers)

def calc_tamura_nei_distance(fasta_data, gap_deletion=True):
    refs = fasta_data['sequences']
    headers = fasta_data['headers']

    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    seq_array = _seqs_to_int_array(refs)
    # Get pairwise counts
    p1_mat, p2_mat, tv_mat, len_mat = _calculate_metrics_vectorized(seq_array, metric_type='tn93')

    N, L_total = seq_array.shape
    dist_mat = np.full((N, N), np.nan)

    batch_size = 50
    for i in range(0, N, batch_size):
        end_i = min(i + batch_size, N)
        batch_seqs = seq_array[i:end_i] # (B, L)

        # Valid mask (B, N, L)
        valid_mask = (batch_seqs[:, None, :] < 4) & (seq_array[None, :, :] < 4)

        # Expand batch_seqs to (B, N, L) via broadcast
        b_expanded = np.broadcast_to(batch_seqs[:, None, :], (end_i-i, N, L_total))
        s_expanded = np.broadcast_to(seq_array[None, :, :], (end_i-i, N, L_total))

        # Helper to count base X in pair
        def get_freq(base_val):
            c1 = (b_expanded == base_val) & valid_mask
            c2 = (s_expanded == base_val) & valid_mask
            return 0.5 * (c1.sum(axis=2) + c2.sum(axis=2))

        # These are (B, N) matrices
        fA = get_freq(0)
        fG = get_freq(1)
        fC = get_freq(2)
        fT = get_freq(3)

        # Now we have everything for the formula for this block
        L = len_mat[i:end_i, :]
        P1 = p1_mat[i:end_i, :] / L
        P2 = p2_mat[i:end_i, :] / L
        Q  = tv_mat[i:end_i, :] / L

        # Avoid div by zero in frequencies
        total_freq = fA + fG + fC + fT # Should equal L

        # Normalised frequencies
        with np.errstate(divide='ignore', invalid='ignore'):
            gA = fA / total_freq
            gG = fG / total_freq
            gC = fC / total_freq
            gT = fT / total_freq

            gR = gA + gG
            gY = gC + gT

            k1 = (2 * gA * gG) / gR
            k2 = (2 * gC * gT) / gY
            k3 = 2 * (gR * gY - (gA * gG * gY / gR) - (gC * gT * gR / gY))

            # Terms
            # Handle small denominators
            term1_arg = 1 - P1 / k1 - Q / (2*gR)
            term2_arg = 1 - P2 / k2 - Q / (2*gY)
            term3_arg = 1 - Q / k3

            # Distance
            d = np.zeros_like(L)

            # Check validity masks
            valid_calc = (total_freq > 0) & (gR > 1e-9) & (gY > 1e-9) & \
                         (k1 > 1e-9) & (k2 > 1e-9) & (k3 > 1e-9) & \
                         (term1_arg > 1e-9) & (term2_arg > 1e-9) & (term3_arg > 1e-9)

            d[valid_calc] = -k1[valid_calc] * np.log(term1_arg[valid_calc]) \
                            -k2[valid_calc] * np.log(term2_arg[valid_calc]) \
                            -k3[valid_calc] * np.log(term3_arg[valid_calc])
                            
            d[~valid_calc] = np.inf
            d[L == 0] = np.nan

            dist_mat[i:end_i, :] = d

    # Diagonal to 0
    np.fill_diagonal(dist_mat, 0.0)

    return pd.DataFrame(dist_mat, index=headers, columns=headers)

if __name__ == "__main__":
    pass
