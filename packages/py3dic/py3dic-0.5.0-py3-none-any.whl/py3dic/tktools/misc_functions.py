import logging
from tkinter import filedialog, messagebox

def show_warning_message(message, callback):
    """ This is a generic method that displays a message 
    """
    if messagebox.askokcancel("Warning", message):
        try:
            logging.debug("User accepted. Executing callback")
            callback()
        except Exception as e:
            logging.debug(str(e))
    else:
        logging.debug("User aborted. Keeping default option")