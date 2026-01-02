import tkinter as tk

class CollapsiblePane(tk.Frame):
    """Pane that collapses and expands 

    Args:
        tk (_type_): _description_
    """    
    # use .content_frame to attach widgets
    def __init__(self, parent, title="", expanded=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.columnconfigure(1, weight=1) # not sure if this works.
        
        self.title_frame = tk.Frame(self)
        self.title_frame.grid(row=0, column=0, sticky="ew")
        self.title_frame.configure(highlightbackground="black", highlightthickness=1)
        
        self.title_label = tk.Label(self.title_frame, text=title, width=30, anchor="w")
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.toggle_button = tk.Button(self.title_frame, text="-", width=2, command=self.toggle)
        self.toggle_button.grid(row=0, column=1, sticky="e")
        
        self.columnconfigure(1, weight = 1)

        self.content_frame = tk.Frame(self)
        # create a bold outline for the content frame
        self.content_frame.configure(highlightbackground="black", highlightthickness=1)
        if expanded:
            self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        self._expanded = expanded
    
    def toggle(self):
        """toggles the state
        """        
        if self._expanded:
            self.content_frame.grid_forget()
            self.toggle_button.configure(text="+")
        else:
            self.content_frame.grid(row=1, column=0, sticky="nsew")
            self.toggle_button.configure(text="-")
        
        self._expanded = not self._expanded

    def set_state(self, expanded_state:bool=None):
        """set the state
    
        Args:
            expanded_state (bool, optional): _description_. Defaults to None.
        """        
        if expanded_state == False:
            self.content_frame.grid_forget()
            self.toggle_button.configure(text="+")
            self._expanded = False
        elif expanded_state:
            self.content_frame.grid(row=1, column=0, sticky="nsew")
            self.toggle_button.configure(text="-")
            self._expanded = True
        else:
            # this should account for None
            pass
            # logging.debug('')
