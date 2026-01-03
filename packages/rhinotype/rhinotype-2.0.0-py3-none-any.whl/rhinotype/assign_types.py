import os
import pandas as pd
import numpy as np
import datetime
from .pairwise_distances import pairwise_distances
import importlib.resources

def assign_types(fasta_data, user_input, model='p-distance', gap_deletion=True, threshold=0.405, 
                 save_report=True, output_dir='reports', user_seq_names=None, distances_matrix=None):
    """
    Assigns types to query sequences based on p-distance to known prototypes.

    Args:
        fasta_data (pd.DataFrame): DataFrame from pairwise_distances input.
        model (str): Distance model (default 'p-distance').
        gap_deletion (bool): Whether to delete gaps (default True).
        threshold (float): Max p-distance for assignment (default 0.105).
        save_report (bool): If True, saves the output DataFrame to a CSV file.
        output_dir (str): Directory to save the report (default 'reports').

    Returns:
        pd.DataFrame: A DataFrame with query, assignedType, distance, and reference.
    """

    # Read prototype sequences
    try:
        # Determine the correct prototype CSV file
        user_input_cap = user_input.capitalize()
        if user_input_cap == 'Vp1':
            prototype_filename = 'vp1_test.csv'
        elif user_input_cap == 'Vp4/2':
            prototype_filename = 'prototypes.csv'
        else:
            raise ValueError("Invalid input. Please specify either 'Vp1' or 'Vp4/2'.")

        # Use importlib.resources to access the data file
        path_obj = importlib.resources.files('rhinotype.data').joinpath(prototype_filename)
        with importlib.resources.as_file(path_obj) as path:
            prototypes_df = pd.read_csv(path)
            
    except FileNotFoundError:
        raise Exception("Error: Failed during genotype assignment. Prototypes file not found. Please check the file path.")

    names_to_keep = prototypes_df['Accession'].tolist()

    # Run pairwiseDistances to calculate distances
    if distances_matrix is not None:
        print("Using pre-calculated distance matrix.")
        distances = distances_matrix.copy() # Use the provided matrix
    else:
        print("Calculating pairwise distances for assign_types...")
        # Run pairwiseDistances to calculate distances
        distances = pairwise_distances(fasta_data, model=model, gap_deletion=gap_deletion)

    # Filter columns based on the prototypes
    distances = distances.loc[:, distances.columns.isin(names_to_keep)]

    # Simplify filtering: Classify everything that is NOT in the 'exclude' list.
    # By default, exclude all known prototypes.
    prototypes_to_exclude = set(names_to_keep)

    # If the user explicitly provides sequences that match known prototypes (e.g. test data), do NOT exclude them.
    if user_seq_names is not None:
        user_names_set = set(user_seq_names)
        # Remove user-provided names from the exclusion list
        prototypes_to_exclude = prototypes_to_exclude - user_names_set
        print(f"User provided {len(user_seq_names)} sequences. {len(prototypes_to_exclude)} prototypes will be excluded from report.")

    # Identify rows to keep (Query sequences)
    # We keep rows that are NOT in the exclusion set
    query_mask = ~distances.index.isin(prototypes_to_exclude)
    distances = distances.loc[query_mask, :]
    
    print(f"Report filtered for {len(distances)} query sequences.")

    # --- Vectorized Assignment Logic ---
    print("Assigning types using vectorized operations...")

    # Create a mask of distances within the threshold
    # Note: Using float comparison, ensure threshold is handled correctly
    valid_mask = distances < threshold

    # Find the *minimum* distance for each row, but ONLY among valid columns
    # If min() is taken, it might be a distance > threshold if no valid ones exist.
    # So replace invalid entries with Infinity before finding min
    distances_for_min = distances.where(valid_mask, np.inf)

    # 1. Find the minimum distance for each query (row)
    min_distances = distances_for_min.min(axis=1)

    # 2. Find the column name (reference) corresponding to the minimum distance
    # idxmin will return the first occurrence of the minimum value
    ref_seqs = distances_for_min.idxmin(axis=1)

    # 3. Determine if a valid assignment exists (min_distance < infinity)
    # If min_distance is inf, it means all values were >= threshold
    has_assignment = min_distances != np.inf

    # Prepare lists/arrays for the output DataFrame
    assigned_types = []

    # Process the ref_seqs to extract the type (e.g. "RV_A1" -> "A1")
    # Use zip to iterate over values directly, avoiding index lookup issues 
    # if there are duplicate index labels (e.g. user input overlapping with prototypes)
    for ref, is_assigned in zip(ref_seqs, has_assignment):
        if is_assigned:
            # Extract type: Assumes format like "..._Type"
            # Matching original logic: .replace("RV", "").split("_")[-1]
            t = ref.replace("RV", "").split("_")[-1]
            assigned_types.append(t)
        else:
            assigned_types.append("unassigned")

    # Fix: Handle all-NaN rows to avoid FutureWarning/ValueError
    # Fill NaN with Inf temporarily so idxmin always finds a valid index (or first one)
    # This prevents the crash if a row is all NaNs.
    distances_filled = distances.fillna(np.inf)
    raw_closest_ref = distances_filled.idxmin(axis=1)

    # Update ref_seqs vector to use the raw closest ref where assignment failed
    final_refs = raw_closest_ref.values

    # The 'assignedType' column gets the clean type or "unassigned"
    # The 'distance' column gets the min distance
    final_distances = min_distances.values.copy()
    final_distances[~has_assignment] = np.nan

    output_df = pd.DataFrame({
        'query': distances.index,
        'assignedType': assigned_types,
        'distance': final_distances,
        'reference': final_refs
    })

    # --- Save Report ---
    if save_report:
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            # Sanitize the region name for the filename (replaces '/' with '_')
            region_name = user_input.capitalize().replace('/', '_')
            # Create a timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Define the filename
            filename = f"classification_report_{region_name}_{timestamp}.csv"
            # Define the full save path
            save_path = os.path.join(output_dir, filename)
            # Save the DataFrame to a CSV file
            output_df.to_csv(save_path, index=False)
            print(f"Classification report successfully saved to: {save_path}")
        except Exception as e:
            print(f"Error saving report: {e}")

    return output_df

if __name__ == "__main__":
    assign_types() 
