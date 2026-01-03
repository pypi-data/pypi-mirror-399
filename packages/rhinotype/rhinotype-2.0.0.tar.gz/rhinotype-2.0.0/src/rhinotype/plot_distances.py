import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pandas as pd

def plot_distances(distances_matrix, region, output_dir=None):
    # Ensure the input is a DataFrame to leverage labels
    if not isinstance(distances_matrix, pd.DataFrame):
        distances_matrix = pd.DataFrame(distances_matrix)

    # Plotting the heatmap
    num_sequences = distances_matrix.shape[0]

    # --- Smart Scaling for Large Datasets ---
    if num_sequences > 100:
        # Large dataset: Show sparse labels (every Nth) to avoid clutter but keep context
        step = int(np.ceil(num_sequences / 50)) # Aim for ~50 labels max
        xticklabels = yticklabels = step
        
        # Cap max size at 40 inches
        fig_size = min(40, max(12, num_sequences * 0.02)) 
        dpi_val = 300 
        font_size = 10 # Readable size for sparse labels
    else:
        # Small/Medium dataset: Show all details
        xticklabels = yticklabels = True
        fig_size = max(18, num_sequences * 0.3)
        dpi_val = 600
        # Dynamic font size
        font_size = max(4, 200 / num_sequences) if num_sequences > 0 else 4
        if font_size > 12: font_size = 12

    plt.figure(figsize=(fig_size, fig_size * 0.8), dpi=dpi_val)
    
    # seaborn's xticklabels parameter can take an int 'step' to plot every n-th label
    sns.heatmap(distances_matrix, cmap='YlOrRd', cbar=True, 
                xticklabels=xticklabels, yticklabels=yticklabels)
    
    plt.title(f"{region} genetic distances between sequences")

    # Rotate labels
    plt.xticks(rotation=90, fontsize=font_size)
    plt.yticks(rotation=0, fontsize=font_size)

    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "distances.png")

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    plot_distances()
