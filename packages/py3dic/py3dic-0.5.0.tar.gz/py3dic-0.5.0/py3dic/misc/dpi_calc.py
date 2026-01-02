#%%
import math

def calculate_dpi_from_fov(resolution_width, fov_horizontal_deg, distance):
    """
    Calculates the DPI required for a screen to cover a specific Field of View
    at a specific viewing distance.
    
    Args:
        resolution_width (int): The number of horizontal pixels (e.g., 1920).
        fov_horizontal_deg (float): The horizontal Field of View in degrees.
        distance (float): The viewing distance in inches.
        
    Returns:
        float: The calculated DPI.
    """
    
    if fov_horizontal_deg >= 180:
        raise ValueError("FOV must be less than 180 degrees for a flat plane calculation.")

    # 1. Convert FOV from degrees to radians for trigonometric functions
    fov_radians = math.radians(fov_horizontal_deg)

    # 2. Calculate the physical width of the screen using trigonometry
    # Formula: Width = 2 * distance * tan(FOV / 2)
    screen_width_inches = 2 * distance * math.tan(fov_radians / 2)

    # 3. Calculate DPI
    # Formula: DPI = Pixels / Inches
    dpi = resolution_width / screen_width_inches

    return dpi, screen_width_inches


def calculate_dpi_from_dimensions(res_x, res_y, width_mm, height_mm):
    """
    Calculates the DPI (Dots Per Inch) given pixel resolution and physical dimensions in millimeters.
    
    Args:
        res_x (int): Horizontal resolution in pixels.
        res_y (int): Vertical resolution in pixels.
        width_mm (float): Physical width of the surface in millimeters.
        height_mm (float): Physical height of the surface in millimeters.
        
    Returns:
        tuple: (dpi_x, dpi_y) as floats. 
               These should be nearly identical for screens with square pixels.
    """
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Physical dimensions must be greater than zero.")

    # Constant: Millimeters in one inch
    MM_PER_INCH = 25.4

    # Convert physical dimensions to inches
    width_inches = width_mm / MM_PER_INCH
    height_inches = height_mm / MM_PER_INCH

    # Calculate DPI
    dpi_x = res_x / width_inches
    dpi_y = res_y / height_inches

    return dpi_x, dpi_y


# --- Example Usage ---

if __name__ == "__main__":
    # Settings
    res_x = 1920          # 1080p Horizontal Resolution
    target_fov = 40       # Desired Field of View in degrees
    viewing_dist = 24     # Distance from eye to screen in inches (approx arm's length)

    try:
        calculated_dpi, width = calculate_dpi_from_fov(res_x, target_fov, viewing_dist)
        
        print(f"--- Configuration ---")
        print(f"Resolution: {res_x} pixels wide")
        print(f"Target FOV: {target_fov} degrees")
        print(f"Distance:   {viewing_dist} inches")
        print(f"-" * 25)
        print(f"Required Screen Width: {width:.2f} inches")
        print(f"Calculated DPI:        {calculated_dpi:.2f} DPI")

    except ValueError as e:
        print(f"Error: {e}")

#%%
if __name__ == "__main__":
    """
    Test a specific metric case.
    Example: 1920x1080 pixels on a 190x100 mm surface.
    """
    res_x, res_y = 1920, 1080
    width_mm, height_mm = 190, 100
    
    # Manual Calc for verification:
    # Width in inches: 190 / 25.4 ~= 7.4803
    # Height in inches: 100 / 25.4 ~= 3.9370
    # DPI X: 1920 / 7.4803 ~= 256.67
    # DPI Y: 1080 / 3.9370 ~= 274.32
    
    dpi_x, dpi_y = calculate_dpi_from_dimensions(res_x, res_y, width_mm, height_mm)
    
    assert dpi_x == pytest.approx(256.67, abs=0.1)
    assert dpi_y == pytest.approx(274.32, abs=0.1)
