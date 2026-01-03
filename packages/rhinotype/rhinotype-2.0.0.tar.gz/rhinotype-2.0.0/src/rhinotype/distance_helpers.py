import math

# --- Internal helper functions for robust counting ---

def _count_substitutions_k2p(seq1, seq2):
    """
    Correctly counts transitions and transversions using pairwise deletion.
    This function is the new core logic for K2P.
    """
    transitions = 0
    transversions = 0
    length = 0

    purines = {'A', 'G'}
    pyrimidines = {'C', 'T'}

    for n1, n2 in zip(seq1, seq2):
        b1 = n1.upper()
        b2 = n2.upper()

        # Pairwise deletion: Skip sites with gaps or ambiguous characters
        if b1 not in "ACGT" or b2 not in "ACGT":
            continue

        length += 1

        if b1 == b2:
            continue

        # Check for transition
        if (b1 in purines and b2 in purines) or \
           (b1 in pyrimidines and b2 in pyrimidines):
            transitions += 1
        # Otherwise, it's a transversion
        else:
            transversions += 1

    # Return length (L), transitions (S), and transversions (V)
    return length, transitions, transversions

def _count_substitutions_tn93(seq1, seq2):
    """
    Correctly counts substitution types and base frequencies for the TN93 model,
    using pairwise deletion. This is the new core logic for TN93.
    """
    p1_transitions = 0  # Purine transitions (A <-> G)
    p2_transitions = 0  # Pyrimidine transitions (C <-> T)
    transversions = 0
    length = 0

    # For calculating base frequencies (average of both sequences)
    freq = {'A': 0, 'C': 0, 'G': 0, 'T': 0}

    purines = {'A', 'G'}
    pyrimidines = {'C', 'T'}

    for n1, n2 in zip(seq1, seq2):
        b1 = n1.upper()
        b2 = n2.upper()
        
        if b1 not in "ACGT" or b2 not in "ACGT":
            continue

        length += 1
        # Count bases for frequency calculation
        # Each base contributes to half the count at that site
        freq[b1] += 0.5
        freq[b2] += 0.5

        if b1 == b2:
            continue

        # Check for purine transition
        if b1 in purines and b2 in purines:
            p1_transitions += 1
        # Check for pyrimidine transition
        elif b1 in pyrimidines and b2 in pyrimidines:
            p2_transitions += 1
        # Otherwise, it's a transversion
        else:
            transversions += 1

    # Return length, transition types, transversions, and frequencies
    return length, p1_transitions, p2_transitions, transversions, freq

# --- Public helper functions (for p-dist and JC69) ---

def calculate_p_distance(seq1, seq2):
    """
    Calculates the p-distance between two DNA sequences using pairwise deletion.
    """
    differences = 0
    length = 0
    for n1, n2 in zip(seq1, seq2):
        b1 = n1.upper()
        b2 = n2.upper()

        # Pairwise deletion
        if b1 not in "ACGT" or b2 not in "ACGT":
            continue

        length += 1
        if b1 != b2:
            differences += 1

    return differences / length if length > 0 else 0.0

def jukes_cantor_distance(p_distance):
    """
    Calculates the Jukes-Cantor distance from a given p-distance.
    """
    if p_distance >= 0.749999: # Use a buffer for float precision
        return float('inf')
    if p_distance == 0.0:
        return 0.0

    arg = 1 - (4/3) * p_distance
    if arg <= 1e-9: # Check for domain error
        return float('inf')

    return -0.75 * math.log(arg)

# --- (NEW) Public Distance Calculation Functions ---

def kimura_distance(seq1, seq2):
    """
    Calculates the Kimura 2-Parameter (K2P) distance.
    This implementation is now robust against mathematical domain errors.
    """
    # Step 1: Get substitution counts using the robust counter
    L, S, V = _count_substitutions_k2p(seq1, seq2)

    if L == 0:
        return 0.0

    # Step 2: Calculate proportions of transitions (P) and transversions (Q)
    P = S / L
    Q = V / L

    # Step 3: CRITICAL - Check for mathematical domain errors before calculation
    arg1 = 1 - 2 * P - Q
    arg2 = 1 - 2 * Q

    if arg1 <= 1e-9 or arg2 <= 1e-9:  # Use a small epsilon for float safety
        return float('inf') # Return infinity if distance is not computable

    # Step 4: Apply the K2P formula
    distance = -0.5 * math.log(arg1) - 0.25 * math.log(arg2)

    return distance

def tamura_nei_distance(seq1, seq2):
    """
    Calculates the Tamura-Nei 93 (TN93) distance.
    This implementation is now robust against mathematical and division-by-zero errors.
    """
    # Step 1: Get detailed counts and frequencies from the robust counter
    L, S1, S2, V, freqs = _count_substitutions_tn93(seq1, seq2)

    if L == 0:
        return 0.0

    # Step 2: Calculate proportions P1, P2, and Q
    P1 = S1 / L  # Purine transitions
    P2 = S2 / L  # Pyrimidine transitions
    Q = V / L

    # Step 3: Calculate base frequencies (already averaged by the counter)
    gA = freqs['A'] / L
    gC = freqs['C'] / L
    gG = freqs['G'] / L
    gT = freqs['T'] / L

    gR = gA + gG  # Frequency of purines
    gY = gC + gT  # Frequency of pyrimidines

    # Step 4: CRITICAL - Handle potential division-by-zero errors
    if gR <= 1e-9 or gY <= 1e-9:
        # Model is not applicable if purines or pyrimidines are missing
        return float('inf')

    k1 = (2 * gA * gG) / gR
    k2 = (2 * gC * gT) / gY
    k3 = 2 * (gR * gY - (gA * gG * gY / gR) - (gC * gT * gR / gY)) # More robust k3

    # Step 5: Check for domain errors
    term1_arg = 1 - P1 / k1 - Q / (2 * gR) if k1 > 1e-9 else 1.0
    term2_arg = 1 - P2 / k2 - Q / (2 * gY) if k2 > 1e-9 else 1.0
    term3_arg = 1 - Q / k3 if k3 > 1e-9 else 1.0

    distance = 0.0

    if k1 > 1e-9 and term1_arg > 1e-9:
        distance += -k1 * math.log(term1_arg)

    if k2 > 1e-9 and term2_arg > 1e-9:
        distance += -k2 * math.log(term2_arg)

    if k3 > 1e-9 and term3_arg > 1e-9:
        distance += -k3 * math.log(term3_arg)

    # Handle cases where terms are not computable but others are
    if (k1 > 1e-9 and term1_arg <= 1e-9) or \
       (k2 > 1e-9 and term2_arg <= 1e-9) or \
       (k3 > 1e-9 and term3_arg <= 1e-9):
        return float('inf')

    return distance
