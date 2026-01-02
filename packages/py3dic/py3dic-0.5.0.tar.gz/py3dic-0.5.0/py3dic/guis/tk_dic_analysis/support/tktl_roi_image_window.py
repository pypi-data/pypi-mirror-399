import tkinter as tk
from PIL import Image, ImageTk
import logging
# TODO: select another image from directory
# TODO: Reset button

class ROIImageWindow(tk.Toplevel):
    WIDTH = 1200
    HEIGHT = 600
    roi:list[tuple] =None
    start_x:int = None # start x position of the roi in pixels
    start_y:int = None # start x position of the roi in pixels
    rect:int = None # rectangle object (canvas.create_rectangle function)

    def __init__(self, master=None, image_path=None, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.image_path = image_path

        self.protocol("WM_DELETE_WINDOW", lambda:logging.debug("Trying to close ROI window- abort"))
        x = self.master.winfo_x() + self.master.winfo_width()
        y = self.master.winfo_y()
        # Set the position of the image window
        logging.debug("%dx%d+%d+%d", self.WIDTH, self.HEIGHT, x, y)
        self.title("Select ROI for DIC analysis")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        self.create_widgets()
        self.reset_params()
        

    def reset_params(self):
        self.roi = None
        self.rect = None
        self.start_x = 0
        self.start_y = 0

    def set_image(self, image_path:str):
        
        if self.image_path == image_path:
            pass            
        else:
            self.reset_params()
            # Load the image
            image = Image.open(image_path)

            # Convert the image to a PhotoImage
            self.photo = ImageTk.PhotoImage(image)

            # Delete the old image from the canvas (if any)
            self.canvas.delete("image") # this deletes only the image
                            # use delete('all') for everything

            # Add the new image to the canvas
            self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
            

    def create_widgets(self):
        # Create a canvas and display the image
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        
        self.canvas.pack()

        # Bind the mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Save the mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if not self.rect:
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline='white',
                width=3
                )

    def on_drag(self, event):
        # Update the rectangle's coordinates to the mouse position
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)
        self.roi = [(int(self.start_x), int(self.start_y)), (int(curX), int(curY))]
        self._update_rectangle()
        self.title(f"Image window ROI: {self.roi[0][0]:d}x{self.roi[0][1]:d}, {self.roi[1][0]:d}x{self.roi[1][1]:d}" )

    def _update_rectangle(self):
        """uses self. roi to draw

        """
        logging.info(f'ROI: {self.roi}')
        logging.info(f'rect: {self.rect}')
        if self.rect is None:
            self.rect = self.canvas.create_rectangle(
                self.roi[0][0], self.roi[0][1], self.roi[1][0], self.roi[1][1],
                outline='white',
                width=3
                )
        # self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
        self.canvas.coords(self.rect, self.roi[0][0], self.roi[0][1], self.roi[1][0], self.roi[1][1])

    def on_button_release(self, event):
        """ on button release event, do something with the roi
        """
        logging.info(f" ROI selection finished: {self.roi}")
        pass  # Here you can add code to do something with the ROI when the mouse button is released
    
    def get_roi(self):
        if self.roi is None:
            assert False, 'no roi selected'
            return None
        else:
            return self.roi
            
# root = tk.Tk()
# win = ROIImageWindow(root, image_path='your_image_path_here')
# root.mainloop()
