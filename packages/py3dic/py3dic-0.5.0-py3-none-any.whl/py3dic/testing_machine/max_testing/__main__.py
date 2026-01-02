# In py3dic/testing_machine/max_testing/__main__.py

import argparse
import tkinter as tk
from tkinter import filedialog
# Import the class from the neighboring file
from .jinan_ut_file_processor import JinanUTFileProcessor

def main():
    """Main function to run the Jinan UT file conversion utility."""
    parser = argparse.ArgumentParser(
        description="Convert a Jinan UT testing machine file to an agnostic format."
    )
    parser.add_argument(
        "filepath",
        nargs="?", # Makes the argument optional
        default=None,
        help="Path to the Jinan UT file. If not provided, a file selection dialog will open."
    )
    args = parser.parse_args()

    file_path = args.filepath

    # If no path is given via command line, open the file dialog
    if not file_path:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(
            title="Select a Jinan UT file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

    if not file_path:
        print("No file selected. Exiting.")
        return

    # Use the processor class to do the work
    print(f"Processing file: {file_path}")
    jfp = JinanUTFileProcessor(file_path)
    jfp.load_data()
    jfp.save_data() # This method already saves in the agnostic format
    
    print("\nConversion complete. Agnostic data saved.")
    print(f"Metadata: {jfp.get_metadata()}")
    print("\nDataFrame head:\n", jfp.get_dataframe().head())


if __name__ == "__main__":
    main()