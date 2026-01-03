import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_frequency(assigned_types_df, region, output_dir=None, show_legend=False):
    # Add 'species' column based on the first letter of 'assignedType'
    assigned_types_df['assignedType'] = assigned_types_df['assignedType'].astype(str)
    assigned_types_df['species'] = assigned_types_df['assignedType'].str[0]

    # Sanitize region name for filenames (e.g., "Vp4/2" -> "Vp4_2")
    region_filename = region.replace('/', '_') 

    # Aggregate counts by assignedType
    types_counts = assigned_types_df.groupby('assignedType').size().reset_index(name='query')
    types_counts['label'] = types_counts['assignedType'] + ', ' + types_counts['query'].astype(str)
    types_counts['species'] = types_counts['assignedType'].str[0]

    # Transform the data frame
    types_counts = types_counts.assign(
        end_y=types_counts['query'].cumsum(),
        start_y=types_counts['query'].cumsum().shift(fill_value=0)
    )

    # Replace species "u" (from "unassigned") with "Other"
    types_counts.loc[types_counts['species'] == 'u', 'species'] = 'Other'

    # Define colors for each species
    color_map = {"A": "blue", "B": "red", "C": "green", "Other": "grey"}
    colors = types_counts['species'].map(color_map).fillna('grey') # Added fillna for safety

    # Plot the bar chart
    num_types = len(types_counts)
    fig_width = max(10, num_types * 0.3)

    plt.figure(figsize=(fig_width, 6), dpi = 600)
    plt.bar(types_counts['assignedType'], types_counts['query'], color=colors)
    plt.title(f"{region} frequency types")
    plt.xlabel("RV Type")
    plt.ylabel("Count")

    if show_legend:
        # Add legend
        plt.legend(handles=[plt.Rectangle((0,0),1,1, color=color_map[key]) for key in color_map],
                   labels=[key for key in color_map], title="Species", loc='upper right')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)

    save_filename = f"{region_filename}_frequency.png"
    save_path = os.path.join(output_dir, save_filename)

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    print("This script is intended to be imported and called from a main script.")
    print("It cannot be run directly without dummy data.")
