#%%
import pathlib
import logging
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from PIL import Image, ImageTk

# TODO: add rotation of image
# TODO: select another image from directory
# TODO: Reset button

logger = logging.getLogger(__name__)

class TLBrowseImageWindow(tk.Toplevel):
    WIDTH = 800
    HEIGHT = 600
    RESULT_OPTIONS = ["marker", "grid", "disp", "strain map (not implemented)"]
    #TODO Implement strain map
    # this requires changes to the pygrid. 

    def __init__(self, master=None, results_folder:str=None, standalone:bool=False,**kwargs):
        """_summary_

        Args:
            master (_type_, optional): _description_. Defaults to None.
            results_folder (str, optional): _description_. Defaults to None.
            standalone (bool, optional): If this is called as standalone up. Defaults to False.
        """        
        super().__init__(master, **kwargs)

        self.master = master
        if results_folder is not None:
            self.results_folder = pathlib.Path(results_folder)
            self._standalone = standalone
        else: 
            self.results_folder = pathlib.Path('.')
            self._standalone = True
        

        self.protocol("WM_DELETE_WINDOW", lambda: logging.debug("Trying to close ROI window- abort"))
        x = self.master.winfo_x() + self.master.winfo_width()
        y = self.master.winfo_y()
        # Set the position of the image window
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        self.title('Browse Results')

        self.create_widgets()
        # self.set_image(self.image_path)

        if not self._standalone:
            self.change_type()  



    def create_widgets(self):
        self._strVar_ResultType = tk.StringVar(master=self, value=self.RESULT_OPTIONS[0])
        self._strVar_ResultType.trace_add(mode='write', callback=lambda *args:self.change_type())
        self._intVar_image_no = tk.IntVar(master=self, value=0)

        # ========================= Label Frame ===============================
        self.lbf_Controls = tk.LabelFrame(master=self, text='Controls')
        self.lbf_Controls.grid(row=1,column=0, sticky='we')

        if self._standalone:
            self.btn_browse_for_folder = tk.Button(self.lbf_Controls,
                text='Browse for folder',
                command=self.browse_for_folder)
            self.btn_browse_for_folder.grid(row=0, column=0, columnspan=3, sticky='we')


        self.cmb_result_type = ttk.Combobox(
            self.lbf_Controls, values=self.RESULT_OPTIONS, 
            state="readonly", 
            textvariable=self._strVar_ResultType,
            postcommand=self.change_type
        )
        self.cmb_result_type.grid(row=1, column=1)

        self.image_no_label = tk.Label(self.lbf_Controls, 
            text="Image No")
        self.image_no_label.grid(row=2, column=0)

        self.image_no_slider = ttk.Scale(
            self.lbf_Controls, from_=1, to=10, 
            variable=self._intVar_image_no,
            orient="horizontal", command=self.update_image
        )
        self.image_no_slider.grid(row=2, column=1)

        # Create a canvas and display the image
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.grid(row=2,column=0)

    def change_type(self):
        """Changes the type of the image presented 
        and update the image based on the current values of the controls
        """        
        self._working_folder = self.results_folder / self.cmb_result_type.get() 
        assert self._working_folder.exists(), ValueError(f'Folder {self._working_folder} does not exist')
        self._working_images =  list(self._working_folder.glob('*'))
        self._number_of_images = len(self._working_images)
        logging.info(f"found {self._number_of_images} images inside folder : {str(self._working_folder)}")
        self.image_no_slider.configure(to=self._number_of_images)
        
        # Attempt to update the image
        self.update_image(None)

    def update_image(self, value:str):
        """responsible for changing the image path

        Args:
            value (str): _description_
        """        
        # logging.info(f' value: {value} of type {type(value)}')
        image_no = self._intVar_image_no.get()
        logging.info(f'Now changing to image no {image_no}' )
        image_path = self._working_images[image_no]
        self._set_image(image_path)

    def _set_image(self, image_path: str):
        """sets the image inside the canvas

        #TODO merge with update image
        currently only used by self.update_image

        Args:
            image_path (str): _description_
        """        
        # Load the image
        image = Image.open(image_path)

        # Convert the image to a PhotoImage
        self.photo = ImageTk.PhotoImage(image)

        # Delete the old image from the canvas (if any)
        self.canvas.delete("image")  # this deletes only the image
                            # use delete('all') for everything

        # Add the new image to the canvas
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')





    def browse_for_folder(self):
        """function responsible for changing working directory
        """        
        results_folder = filedialog.askdirectory(initialdir=str(self.results_folder), mustexist=True, title="Select a folder that contains DIC results:")
        self.results_folder = pathlib.Path(results_folder)
        self.change_type()

    def set_results_folder(self, path_to_folder:pathlib.Path=None):
        """accessor function that sets the results folder (useful externally)

        Args:
            path_to_folder (pathlib.Path, optional): _description_. Defaults to None.
        """        
        assert path_to_folder.exists(), f"ValueError: Path {str(path_to_folder)} :does not exist"
        assert isinstance(path_to_folder, pathlib.Path), f"ValueError: Path {str(path_to_folder)} is not pathlib.Path"
        self.results_folder = path_to_folder
#%%
if __name__=="__main__":     
    print(pathlib.Path.cwd())
    RES_PATH = pathlib.Path("examples\\imada_ut\\output\\pydic_20230715-1730\\")
    print(RES_PATH.exists())
    RES_PATH = RES_PATH if RES_PATH.exists() else pathlib.Path('.')
    assert RES_PATH.exists(), "this is not a valid folder"
    root = tk.Tk()
    win = TLBrowseImageWindow(root, results_folder=str(RES_PATH), standalone=True)
    root.mainloop()

# %%
