import tkinter as tk


class FileBrowseEntry(tk.Frame):
    """A custom Tkinter Frame widget for file browsing functionality.

    This class combines a Label, Entry, and Button to create a file browsing
    widget within a Tkinter application.

    Attributes:
        label (tk.Label): The label widget displaying the description.
        entry (tk.Entry): The entry widget displaying the selected file path.
        button (tk.Button): The button widget to trigger the file browsing action.

    Args:
        parent (tk.Widget): The parent widget to which this frame belongs.
        label_text (str): Text to display on the label.
        button_text (str): Text to display on the button.
        browse_command (callable): Function to execute when the button is clicked.
        textvariable (tk.StringVar): Text variable for the Entry widget.
        label_width (int, optional): Width of the label. Defaults to 10.
        *args: Additional positional arguments for the tk.Frame superclass.
        **kwargs: Additional keyword arguments for the tk.Frame superclass.

    Example:
        >>> root = tk.Tk()
        >>> text_var = tk.StringVar()
        >>> file_entry = FileBrowseEntry(root, "File:", "Browse", some_command, text_var)
        >>> file_entry.pack()
    """
    def __init__(self, parent, label_text, button_text, browse_command, textvariable, label_width=10,*args, **kwargs):
        super().__init__(parent)

        # Configure the grid to allow resizing
        self.grid_columnconfigure(1, weight=1)

        self.label = tk.Label(self, text=label_text, width=label_width)
        self.label.grid(row=0, column=0)

        self.entry = tk.Entry(self, state='readonly', textvariable=textvariable)
        self.entry.grid(row=0, column=1, sticky='ew')

        self.button = tk.Button(self, text=button_text, command=browse_command)
        self.button.grid(row=0, column=2)

    
    def set_browse_command(self, new_command:callable):
        """ function that sets the browse command 
        
        this is used to update the browse command, or set it from the controller after initialisation
        """
        self.button.config(command=new_command)
    
    def set_button_state(self, state:str):
        """Function that sets the state of the button"""
        if state in ["normal", "disabled"]:
            self.button.config(state=state)