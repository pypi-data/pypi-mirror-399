#%%
# import inspect
import pathlib
import tkinter as tk

import logging
logger = logging.getLogger(__name__)
# Assuming the Camera and ImageCapturingExperiment classes are defined elsewhere
from .mvc_controller_dic import tkapp_DIC_Controller
#%%

def _tk_app_dic_starter(script_dir):
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_Controller(root, starting_dir=script_dir)
    root.mainloop()

# def tkapp_dic_light_stack():
#     """starting the Capture only app 
#     """    
#     # Get the second frame from the top of the stack (the caller of this function)
#     caller_frame = inspect.stack()[1]
#     script_dir = pathlib.Path(caller_frame.filename).resolve().parent
#     _tk_app_dic_starter(script_dir)

# def tkapp_dic_light_dummy_func(caller_func):
#     """starting the app 
#     using a dummy caller func

#     Args:
#         caller_func (function): dummy function used only to get the script filename 
#     """    
#     script_dir = pathlib.Path(inspect.getfile(caller_func)).resolve().parent
#     _tk_app_dic_starter(script_dir)


def tk_analysis_app_launcher():
    """ Used for entry point in setup.py
    """
    # Determine the script directory
    script_dir = pathlib.Path(__file__).resolve().parent
    print(f"Script directory: {script_dir}")
    
    # Initialize the Tkinter root and application
    root = tk.Tk()
    app = tkapp_DIC_Controller(root, starting_dir=script_dir)
    root.mainloop()


def tk_dic_full_launcher():
    """ Used for entry point in setup.py for the full interface (analysis and merge)
    """
    # Determine the script directory
    script_dir = pathlib.Path(__file__).resolve().parent
    print(f"Script directory: {script_dir}")
    
    # Initialize the Tkinter root and application
    root = tk.Tk()
    app = tkapp_DIC_Controller(root, starting_dir=script_dir, full_interface=True)
    root.mainloop()



if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_Controller(root, starting_dir=script_dir)
    root.mainloop()


# %%
