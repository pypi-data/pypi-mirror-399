#%%
# import inspect
import pathlib
import tkinter as tk

import logging
logger = logging.getLogger(__name__)
# Assuming the Camera and ImageCapturingExperiment classes are defined elsewhere
from py3dic.guis.tk_merge_dic_ut.mvc_controller_dic_ut import tkapp_DIC_UT_merge_Controller
#%%

def _tk_app_dic_starter(script_dir):
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_UT_merge_Controller(root, starting_dir=script_dir)
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


def tk_merge_launcher():
    """ Used for entry point in setup.py
    """
    # Determine the script directory
    script_dir = pathlib.Path(__file__).resolve().parent
    logging.info(f"Starting directory: {script_dir}")
    
    # Initialize the Tkinter root and application
    root = tk.Tk()
    app = tkapp_DIC_UT_merge_Controller(root, starting_dir=script_dir)
    root.mainloop()

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_UT_merge_Controller(root, starting_dir=script_dir)
    root.mainloop()


# %%
