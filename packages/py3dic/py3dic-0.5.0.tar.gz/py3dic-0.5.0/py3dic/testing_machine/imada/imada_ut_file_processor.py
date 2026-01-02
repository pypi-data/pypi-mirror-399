#%%
import pathlib
import pandas as pd
import py3dic.testing_machine.agnostic as agnostic
from typing import Dict, Tuple

class ImadaUTFileProcessor:
    data_df: pd.DataFrame = None
    metadata: Dict = None
    decimation: int = 100  # Default decimation factor
    def __init__(self, filename: str):
        """
        Initialize the processor with a filename.
        
        Args:
            filename (str): Path to the input file to be processed.
        """
        self.filename = pathlib.Path(filename)
        self.metadata = None
        self.data_df = None
        
    def load_data(self, decimation= None) -> Tuple[Dict, pd.DataFrame]:
        """
        Reads imada csv file and returns a decimated Dataframe

            with columns 	
                - force_N	
                - disp_mm	
                - time_s

            Args:
                fname (pathlib.Path|str): imada csv export (from z3a file)
                decimation (int, optional): reduce the data by the decimation factor. Defaults to 100.

        Returns:
            Tuple[Dict, pd.DataFrame]: A tuple containing the metadata dictionary 
                                      and the processed data DataFrame.

        """
        COLNAMES = agnostic.AGNOSTIC_COLNAMES
        # obtain the meta data 
        df_ut_meta = pd.read_csv(self.filename, sep="=",nrows=13, header=None, index_col=0, names=["Description", "Value"])
        RECORDING_DT = float(df_ut_meta.loc['RECORDING RATE ','Value'].strip()[:-1])
        # Covert the df_ut_meta to a dictionary using the Description as keys and Value as values
        self.metadata = df_ut_meta.to_dict(orient='index')
        self.metadata = {k.strip(): v['Value'] for k, v in self.metadata.items()}        
        # obtain the dataframe of the test
        df_ut = pd.read_csv(self.filename, skiprows=13, names = ["Force (N)", "Disp (mm)"])
        df_ut['time_s'] = df_ut.index*RECORDING_DT
        # df_ut.head()
        self.data_df = df_ut.iloc[::decimation,:]
        self.data_df.columns = COLNAMES
        return (self.metadata, self.data_df)
    
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
        # self.data_df[['Load', 'Elong', 'Time']].to_csv(autd_file, index=False, sep="\t")
        
        # Create agnostic tensile data files
        agnostic.create_agnostic_tensile_data_files(
            self.data_df, 
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
# %%
