import pathlib
import pandas as pd

def read_imada_csv(fname:pathlib.Path|str, decimation:int=100)->pd.DataFrame:
    """Reads imada csv file and returns a decimated Dataframe

    with columns 	
        - force_N	
        - disp_mm	
        - time_s

    Args:
        fname (pathlib.Path|str): imada csv export (from z3a file)
        decimation (int, optional): reduce the data by the decimation factor. Defaults to 100.

    Returns:
        pd.DataFrame: a Dataframe containing columns = ["force_N", "disp_mm", "time_s"]
    """
    COLNAMES = ["force_N", "disp_mm", "time_s"]
    # obtain the meta data 
    df_ut_meta = pd.read_csv(fname, sep="=",nrows=13, header=None, index_col=0, names=["Description", "Value"])
    RECORDING_DT = float(df_ut_meta.loc['RECORDING RATE ','Value'].strip()[:-1])
    # obtain the dataframe of the test
    df_ut = pd.read_csv(fname, skiprows=13, names = ["Force (N)", "Disp (mm)"])
    df_ut['Time (s)'] = df_ut.index*RECORDING_DT
    # df_ut.head()
    df_decimated = df_ut.iloc[::decimation,:]
    df_decimated.columns = COLNAMES
    return df_decimated


def decimate_imada_csv(fname: pathlib.Path | str, decimation: int = 100) -> None:
    """Decimates an imada csv file and saves it with updated metadata and suffix "_decim.csv".

    Args:
        fname (pathlib.Path | str): Original imada csv export (from z3a file).
        decimation (int, optional): Decimation factor to reduce the data. Defaults to 100.
    """
    # Read metadata
    df_ut_meta = pd.read_csv(fname, sep="=", nrows=13, header=None, index_col=0, names=["Description", "Value"])
    original_recording_rate = float(df_ut_meta.loc['RECORDING RATE ', 'Value'].strip()[:-1])
    original_data_count = int(df_ut_meta.loc['DATA COUNT ', 'Value'].strip()[:-1])

    # Update metadata
    df_ut_meta.loc['RECORDING RATE ', 'Value'] = f"{original_recording_rate * decimation},"
    df_ut_meta.loc['DATA COUNT ', 'Value'] = f"{original_data_count // decimation},"

    # Read data and decimate
    df_ut = pd.read_csv(fname, skiprows=13, names=["Force (N)", "Disp (mm)"])
    df_decimated = df_ut.iloc[::decimation, :]

    # Save metadata and decimated data to new file
    new_fname = str(fname).replace('.csv', '_decim.csv')
    with open(new_fname, 'w') as f:
        for index, row in df_ut_meta.iterrows():
            f.write(f"{index}={row['Value']}\n")
        for index, row in df_decimated.iterrows():
            f.write(f"{row['Force (N)']},{row['Disp (mm)']}\n")
        # df_ut_meta.to_csv(f, sep='=', header=False)
        # df_decimated.to_csv(f, header=False, index=False)

