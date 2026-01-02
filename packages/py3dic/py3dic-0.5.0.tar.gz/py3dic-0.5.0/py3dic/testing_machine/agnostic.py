#%% 
import pathlib
import numpy as np
import pandas as pd

AGNOSTIC_COLNAMES  = ["force_N", "disp_mm", "time_s"]


def create_agnostic_tensile_data_files(data_df, metadata, filename_stem, output_dir  =None):
    """
    Takes a suitably formatted dataframe and produces the agnostic files 

    The datafame should have the columns as defined in the AGNOSTIC_COLNAMES.

    Args:
        data_df (pd.DataFrame): The input data DataFrame.
        metadata (dict): The metadata dictionary.
        filename_stem (str): The stem of the filename for output files.
        output_dir (str, optional): The directory to save output files.

    Returns:
        None
    """
    required_columns = AGNOSTIC_COLNAMES    
    try:
        # Check if the required columns exist in the DataFrame    
        for col in required_columns:
            if col not in data_df.columns:
                raise ValueError(f"Column '{col}' is missing from the DataFrame.")
    except ValueError as e:
        print(f"Error: {e}")
        return
    # Create a new DataFrame with the desired columns
    data_df = data_df[required_columns]
    
    # Save the metadata and data files
    if output_dir is None:
        output_dir = pathlib.Path(".")
    
    metadata_file = output_dir / (filename_stem + "_ut.json")
    metadata_df = pd.DataFrame(metadata, index=[0])
    metadata_df.to_json(metadata_file, orient='records', lines=True)
    
    data_file = output_dir / (filename_stem + ".autd")
    data_df.to_csv(data_file, index=False, sep="\t")