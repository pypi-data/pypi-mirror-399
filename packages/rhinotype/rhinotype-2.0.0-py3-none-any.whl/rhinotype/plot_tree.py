import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import os

def plot_tree(distance_matrix, region, output_dir=None):
    # Extract labels if the input is a pandas DataFrame
    labels = None
    if hasattr(distance_matrix, 'index'):
        labels = distance_matrix.index.tolist()

    # Convert the data to a numpy array for calculations
    dm_array = np.array(distance_matrix)

    # Convert the symmetric distance matrix to a condensed distance matrix
    condensed_distance_matrix = squareform(dm_array)

    # Perform hierarchical clustering using complete linkage
    hc = linkage(condensed_distance_matrix, method='complete')

    # Plot the dendrogram
    num_leaves = len(dm_array)

    # Dynamic scaling for large trees to avoid Matplotlib backend crashes
    # 0.2 inch per leaf is good for small trees, but too big for 1000+
    scale_per_leaf = 0.2 if num_leaves < 200 else 0.1
    fig_height = max(8, num_leaves * scale_per_leaf)

    # Cap height to avoid "Image size of ... pixels is too large" errors
    # Matplotlib often has a limit around 2^16 (65536) pixels.
    # At 300 DPI, 200 inches is 60000 pixels.
    MAX_HEIGHT_INCHES = 200
    if fig_height > MAX_HEIGHT_INCHES:
        fig_height = MAX_HEIGHT_INCHES
        print(f"Warning: Tree height capped at {MAX_HEIGHT_INCHES} inches to prevent overflow.")

    # Adjust DPI based on size
    dpi = 600
    if num_leaves > 200:
        dpi = 300
    if num_leaves > 1000:
        dpi = 150

    plt.figure(figsize=(15, fig_height), dpi=dpi)
    dendrogram(hc, orientation='left', labels=labels, leaf_font_size=8)

    plt.title(f"{region} simple tree ({num_leaves} sequences)")
    plt.xlabel("Genetic distance")
    plt.ylabel("")
    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "tree.png")

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    plot_tree()
