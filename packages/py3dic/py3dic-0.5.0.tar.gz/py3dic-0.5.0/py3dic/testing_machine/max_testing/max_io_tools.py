import numpy as np
import pandas as pd
#%%
def extract_data_from_file(filename):
    """
    Extract metadata and dataframe data from a file.
    
    This function:
    1. Opens a file with the given filename
    2. Reads incrementally until the line containing "-----------Curve----------" 
    3. Stores metadata up to that line in a dictionary
    4. Uses pandas to read the remaining data as a dataframe
    
    Args:
        filename (str): Path to the file to be processed
        
    Returns:
        tuple: (metadata_dict, dataframe)
            - metadata_dict: Dictionary containing metadata (keys and values separated by tabs)
            - dataframe: Pandas DataFrame containing the curve data
    """
    
    metadata_dict = {}
    curve_marker = "-----------Curve----------"
    curve_line_index = None
    
    # Read the file incrementally to find the curve marker and extract metadata
    with open(filename, 'r') as file:
        for i, line in enumerate(file):
            if curve_marker in line:
                curve_line_index = i
                break
            
            # Skip blank lines
            if line.strip() == "":
                continue
            
            # Process metadata lines (key-value pairs separated by tabs)
            if '\t' in line:
                parts = line.strip().split('\t', 1)  # Split on first tab only
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    metadata_dict[key] = value
    
    # If the curve marker wasn't found, return only metadata
    if curve_line_index is None:
        print("Warning: Curve marker not found in file. Returning only metadata.")
        return metadata_dict, None
    
    # Read the dataframe part using pandas, skipping all lines up to curve_line_index + 1
    df = pd.read_csv(filename, skiprows=curve_line_index+1, sep='\t')
    
    return metadata_dict, df

#%% 
if __name__ == "__main__":
    import os
    
    # Example usage
    filename = os.path.join(os.path.dirname(__file__), 'example.txt')
    
    metadata, df = extract_data_from_file(filename)
    
    print("Metadata:")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    
    if df is not None:
        print("\nDataframe:")
        print(df.head())
