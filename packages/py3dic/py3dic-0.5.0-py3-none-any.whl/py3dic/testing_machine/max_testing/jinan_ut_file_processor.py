import pathlib
import pandas as pd

import tkinter as tk 
from tkinter import filedialog

import py3dic.testing_machine.max_testing as max_io
import py3dic.testing_machine.agnostic as agnostic
from typing import Dict, Tuple

class JinanUTFileProcessor:
    def __init__(self, filename: str):
        """
        Initialize the processor with a filename.
        
        Args:
            filename (str): Path to the input file to be processed.
        """
        self.filename = pathlib.Path(filename)
        self.metadata = None
        self.data_df = None
        
    def load_data(self) -> Tuple[Dict, pd.DataFrame]:
        """
        Load and process the data from the file.
        
        Returns:
            Tuple[Dict, pd.DataFrame]: A tuple containing the metadata dictionary 
                                      and the processed data DataFrame.
        """
        self.metadata, self.data_df = max_io.extract_data_from_file(str(self.filename))
        return self.metadata, self.data_df

    def convert_to_agnostic_format(self) -> pd.DataFrame:
        """
        Convert the loaded data to an agnostic format.
        
        Returns:
            pd.DataFrame: The processed data in agnostic format.
        """
        if self.data_df is None:
            self.load_data()
        
        _df = self.data_df[['Load', 'Elong', 'Time']].rename(
            columns={
                'Load': agnostic.AGNOSTIC_COLNAMES[0],
                'Elong': agnostic.AGNOSTIC_COLNAMES[1],
                'Time': agnostic.AGNOSTIC_COLNAMES[2]
            }
        )
        
        return _df

    def save_data(self, output_dir: str = None) -> Tuple[pathlib.Path, pathlib.Path]:
        """
        Save the processed data to JSON and AUTD files.
        
        Args:
            output_dir (str, optional): Directory to save the files. Defaults to 
                                      filename's parent directory / "data_tensile".
                                      
        Returns:
            Tuple[pathlib.Path, pathlib.Path]: Paths to the saved JSON and AUTD files.
        """
        if self.metadata is None or self.data_df is None:
            self.load_data()
            
        if output_dir is None:
            output_dir = self.filename.parent / "data_tensile"
        else:
            output_dir = pathlib.Path(output_dir)
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # # Save metadata to JSON
        # json_file = output_dir / (self.filename.stem + "_ut.json")
        # metadata_df = pd.DataFrame(self.metadata, index=[0])
        # metadata_df.to_json(json_file, orient='records', lines=True)
        
        # # Save data to AUTD file
        # autd_file = output_dir / (self.filename.stem + ".autd")
        # _df = self.convert_to_agnostic_format()
        # _df.to_csv(autd_file, index=False, sep="\t")

        # Create agnostic tensile data files
        agnostic.create_agnostic_tensile_data_files(
            self.convert_to_agnostic_format(), 
            self.metadata, 
            filename_stem=self.filename.stem, 
            output_dir=output_dir
        )
        
    
    def get_metadata(self) -> Dict:
        """Return the metadata dictionary."""
        if self.metadata is None:
            self.load_data()
        return self.metadata
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return the processed data DataFrame."""
        if self.data_df is None:
            self.load_data()
        return self.data_df
    


def convert_jinan_to_agnostic():
    """tk filedial which wraps the main functionality of converting 
    Jinan UT files to agnostic format.

    This function opens a file dialog to select a Jinan UT file, processes it,
    and saves the converted data in an agnostic format.
    It prints the metadata and the head of the DataFrame for verification.
    
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(
        title="Select a Jinan UT file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    jfp = JinanUTFileProcessor(file_path)
    metadata, data_df = jfp.load_data()
    
    print("Metadata:", metadata)
    print("DataFrame head:\n", data_df.head())

    jfp.save_data()
    jfp.convert_to_agnostic_format()
    print("Conversion complete. Data saved in agnostic format.")