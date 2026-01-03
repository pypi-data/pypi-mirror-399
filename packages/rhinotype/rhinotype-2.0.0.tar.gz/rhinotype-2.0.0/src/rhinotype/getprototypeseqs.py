import os
import shutil
import importlib.resources

def getprototypeseqs(user_input, destinationFolder="RVRefs"):
    """
    Copies the appropriate prototype FASTA file (VP1 or VP4/2) 
    into the user's current working directory inside 'RVRefs'
    as 'RVRefs.fasta'.

    Parameters
    ----------
    user_input : str
        The region of interest ("Vp1" or "Vp4/2").
    destinationFolder : str, optional
        The folder to copy the reference FASTA into (default: "RVRefs").
    """

    user_input = user_input.capitalize().strip()
    ref_name = "RVRefs.fasta"

    # Determine prototype file name
    if user_input == "Vp1":
        prototype_filename = 'vp1_prototypes.fasta'
    elif user_input == "Vp4/2":
        prototype_filename = 'prototypes.fasta'
    else:
        raise ValueError("Invalid input. Please specify either 'Vp1' or 'Vp4/2'.")

    # Use importlib.resources to get a path to the data file
    source_path_obj = importlib.resources.files('rhinotype.data').joinpath(prototype_filename)

    # Destination: in the current working directory (user's context)
    user_cwd = os.getcwd()
    destination_dir = os.path.join(user_cwd, destinationFolder)

    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, ref_name)

    # Copy the selected prototype FASTA file
    with importlib.resources.as_file(source_path_obj) as source_path:
        shutil.copyfile(source_path, destination_file)
        
    print(f"The reference sequence has been copied to '{destination_file}'.")
    return destination_file

if __name__ == "__main__":
    # Ask only once when running directly from terminal
    user_query = input("Do you have VP1 or VP4/2 sequence? (Vp1 or Vp4/2): ")
    user_query = user_query.capitalize().strip()
    getprototypeseqs(user_query)
