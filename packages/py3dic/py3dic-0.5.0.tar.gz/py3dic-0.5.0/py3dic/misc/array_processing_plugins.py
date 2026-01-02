#%%
import numpy as np
from ..dic.core.dic_enums import EnumDataSelection

class ArrayProcessingPlugin:
    name:str = None
    def process(self, array: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Plugins must implement the `process` method.")
    
    #TODO Consider adding a method to return the plugin's name so that it can be saved in the metadata of the processed data

class DefaultBorderRemovalPlugin(ArrayProcessingPlugin):
    """this code removes the border of an array

    Args:
        ArrayProcessingPlugin (_type_): _description_
    """
    name = "Array Border Removal Plugin"
    def process(self, array: np.ndarray) -> np.ndarray:
        assert array.ndim == 2, "array should be 2d"
        assert array.shape[0] > 3 and array.shape[1] > 3, "array should have more than 3 elements in each direction"
        return array[1:-1, 1:-1]

class PortionSelectionPlugin_20(ArrayProcessingPlugin):
    """This code selects a portion of the array	

    args:
        fraction (float): fraction of the array to drop (0 none, 0.5 all)
    """
    name:str = "Portion Selection Plugin"
    fraction:float = 0.2
    def __init__(self):
        self.name = f"Portion Selection Plugin (fraction={self.fraction})"

    def process(self, array: np.ndarray) -> np.ndarray:
        xmax, ymax = array.shape
        x_start, x_end = np.floor(self.fraction * xmax).astype('int'), np.ceil((1 - self.fraction) * xmax).astype('int')
        y_start, y_end = np.floor(self.fraction * ymax).astype('int'), np.ceil((1 - self.fraction) * ymax).astype('int')
        return array[x_start:x_end, y_start:y_end]
    
class PortionSelectionPlugin_40(ArrayProcessingPlugin):
    """This code selects a portion of the array	

    args:
        fraction (float): fraction of the array to drop (0 none, 0.5 all)
    """
    name:str = "Portion Selection Plugin"
    fraction:float = 0.40
    def __init__(self):
        self.name = f"Portion Selection Plugin (fraction={self.fraction})"

    def process(self, array: np.ndarray) -> np.ndarray:
        xmax, ymax = array.shape
        x_start, x_end = np.floor(self.fraction * xmax).astype('int'), np.ceil((1 - self.fraction) * xmax).astype('int')
        y_start, y_end = np.floor(self.fraction * ymax).astype('int'), np.ceil((1 - self.fraction) * ymax).astype('int')
        return array[x_start:x_end, y_start:y_end]

class SelectAllArrayPlugin(ArrayProcessingPlugin):
    """This is trivial but it imitates the process of the original code

    Args:
        ArrayProcessingPlugin (_type_): _description_

    Returns:
        _type_: _description_
    """
    name:str = "Select All Array Plugin"
    
    def process(self, array: np.ndarray) -> np.ndarray:
        return array
    


class PluginFactory:
    def __init__(self):
        self.plugins = {
            # it is important to set the value of the Enum as the key
            EnumDataSelection.REMOVE_BORDER.value : DefaultBorderRemovalPlugin,
            EnumDataSelection.PORTION0_20.value : PortionSelectionPlugin_20,
            EnumDataSelection.PORTION0_40.value : PortionSelectionPlugin_40,
            EnumDataSelection.SELECT_ALL.value : SelectAllArrayPlugin
        }

    def register_plugin(self, name: str, plugin: ArrayProcessingPlugin):
        """Additional plugins may be registered at runtime

        Args:
            name (str): _description_
            plugin (ArrayProcessingPlugin): _description_
        """
        self.plugins[name] = plugin

    def get_plugin(self, name: str) -> ArrayProcessingPlugin:
        plugin = self.plugins.get(name)
        if plugin is None:
            raise ValueError(f"Plugin '{name}' not found")
        return plugin()
    
    """ example usageof PluginFactory in a Tkinter GUI
    import tkinter as tk
    from tkinter import ttk

    def on_selection_change(event):
        selected_plugin_name = combo.get()
        plugin = factory.get_plugin(selected_plugin_name)
        # Use the plugin instance as needed
        # e.g., df_with_time = dic_processor.get_df_with_time(plugin, save_to_file=True)

    factory = PluginFactory()
    factory.register_plugin("Default Border Removal", DefaultBorderRemovalPlugin)
    factory.register_plugin("Portion Selection", PortionSelectionPlugin(fraction=0.1))

    root = tk.Tk()
    combo = ttk.Combobox(root, values=list(factory.plugins.keys()))
    combo.bind("<<ComboboxSelected>>", on_selection_change)
    combo.pack()
    root.mainloop()

    
    """
# arr_plugin_factory = PluginFactory()
# arr_plugin_factory.register_plugin("Default Border Removal", DefaultBorderRemovalPlugin)
# arr_plugin_factory.register_plugin("Portion Selection", PortionSelectionPlugin)
# arr_plugin_factory.register_plugin("Select All Array", SelectAllArrayPlugin)
#
# %%
