#%%
from pathlib import Path
import cv2
import numpy as np
import pytest
from py3dic.dic.rolling_processing.rolling_image_marker_tracker import \
    RollingImageMarkerTracker
from py3dic.dic.core.dic_grid import GridSize

def expected_output_from_text_file():
    """This is a function that returns the text

    Returns:
        _type_: _description_
    """    
    expected_list =[]
    expected_list.append('310.0	370.0	3	90\n')
    expected_list.append('125.0	185.0	3	90\n')
    expected_list.append('example_imgs\Cam_00001.png	310.0,125.0	310.0,155.0	310.0,185.0	340.0,125.0	340.0,155.0	340.0,185.0	370.0,125.0	370.0,155.0	370.0,185.0	\n')
    expected_list.append('example_imgs\Cam_00002.png	298.3341,122.18497	298.3723,152.15681	298.4278,182.1235	328.31256,122.13837	328.93542,152.09497	331.95428,181.95987	366.49072,122.33831	366.2348,152.12717	367.20053,182.06662	\n')
    expected_list.append('example_imgs\Cam_00003.png	294.31274,120.31217	294.36188,150.2475	294.4289,180.19241	324.32007,120.28953	324.9439,150.20859	327.96042,180.04742	362.5801,120.57312	362.30026,150.29019	363.25345,180.2068	\n')
    expected_list.append('example_imgs\Cam_00004.png	286.45355,121.862854	285.9082,150.56247	287.31647,179.79524	313.49612,122.15488	317.11325,151.68886	317.14874,181.11569	353.6328,123.840576	352.35358,152.98993	356.1251,182.6779	\n')

    return expected_list

def expected_values_from_text_file():
    """This is a function that returns the text

    Returns:
        _type_: _description_
    """    
    expected_values = []
    expected_list = expected_output_from_text_file()
    expected_values.append(np.array(expected_list[0].strip().split("\t"), dtype='float'))
    expected_values.append(np.array(expected_list[1].strip().split("\t"), dtype='float'))
    for k in  range(2, len(expected_list)):
        vals = expected_list[k].strip().replace(',','\t').split("\t")
        expected_values.append(np.array(vals[1:], dtype='float32'))
    return expected_values

#%%

def read_test_results_file(filepath):
    """helper function that 

    Args:
        filepath (_type_): _description_

    Returns:
        _type_: _description_
    """    
    with open(filepath, "r") as file:
        lines = file.readlines()
    return lines

def _process_line(line: str) -> str:
    """ this function is used to strip the absolute path in the image file
    which is a sideeffect of the testing process. 
    """
    parts = line.split("\t")
    try:
        float(parts[0])
        return line
    except ValueError:
        pass
    filepath = Path(parts[0])
    stripped_filepath = f"{filepath.parent.name}\\{filepath.name}"
    return "\t".join([str(stripped_filepath)] + parts[1:])


#%%
def test_single_image_displacement_processor():
    current_file_dir = Path(__file__).resolve().parent
    test_images_dir = current_file_dir / "example_imgs"


    win_size_px = (90, 90)
    grid_size_px = (30, 30)
    area_of_interest = ((310, 125), (371, 191))
    
    assert (test_images_dir/"Cam_00001.png").exists()
    ref_img = cv2.imread(str(test_images_dir/"Cam_00001.png"), cv2.IMREAD_GRAYSCALE)
    
    sidp = RollingImageMarkerTracker(reference_image=ref_img,
        win_size_px = win_size_px, 
        grid_size_px = grid_size_px, 
        area_of_interest= area_of_interest,
        verbosity=0)
    a = sidp.dic_parameters()
    b= expected_values_from_text_file()
    np.testing.assert_equal(list(a.values())[:4], b[0])
    np.testing.assert_equal(list(a.values())[4:], b[1])
    
    # Perform additional checks on the contents of the results file
    # # depending on your specific use case and expected output.
    # expected_list = expected_output_from_text_file()
    for k in range(2, 5):
        img = cv2.imread(str(test_images_dir/f"Cam_0000{k}.png"), cv2.IMREAD_GRAYSCALE)
        res = sidp.process_image(img)
        resval = res['point_to_process'].flatten()
        np.testing.assert_allclose(resval , b[k+1], rtol=1e-7)
 
    # file_content = read_test_results_file(result_file)

    # for e,a in zip(expected_list, file_content):
    #     assert e==a, "error"
 

 
def test_get_dic_gridsize_type():
    ref_image = np.ones((100, 100))
    processor = RollingImageMarkerTracker(
        reference_image=ref_image, 
        win_size_px=(10, 10), 
        grid_size_px=(20, 20),
        area_of_interest=[(20,20),(60,70)],  verbosity=0)
    result = processor.get_dic_gridsize()
    assert isinstance(result, GridSize), "Output type should be GridSize"

def test_get_dic_gridsize_value():
    ref_image = np.ones((100, 100))
    processor = RollingImageMarkerTracker(
        reference_image=ref_image,
        win_size_px=(10, 10), 
        grid_size_px=(20, 20),
        area_of_interest=[(0,0),(90,90)], 
        verbosity=0)
    result = processor.get_dic_gridsize()

    # Assuming the values based on ref_image and win_size, grid_size
    expected = GridSize(xmin=0, xmax=80, xnum=5, win_size_x=10, 
                        ymin=0, ymax=80, ynum=5, win_size_y=10)

    assert result.xmin == expected.xmin, "xmin value is not matching"
    assert result.xmax == expected.xmax, "xmax value is not matching"
    assert result.xnum == expected.xnum, "xnum value is not matching"
    assert result.win_size_x == expected.win_size_x, "win_size_x value is not matching"
    assert result.ymin == expected.ymin, "ymin value is not matching"
    assert result.ymax == expected.ymax, "ymax value is not matching"
    assert result.ynum == expected.ynum, "ynum value is not matching"
    assert result.win_size_y == expected.win_size_y, "win_size_y value is not matching"
    
if __name__ == "__main__":
    test_single_image_displacement_processor()

# %%
if __name__ == "__main__":
    test_images_dir = Path("example_imgs")
    image_pattern = str(test_images_dir / "*.png")

    win_size_px = (90, 90)
    grid_size_px = (30, 30)
    area_of_interest = ((310, 125), (371, 191))
    assert (test_images_dir/"Cam_00001.png").exists()
    ref_img = cv2.imread(str(test_images_dir/"Cam_00001.png"), cv2.IMREAD_GRAYSCALE)
    
    sidp = RollingImageMarkerTracker(reference_image=ref_img,
        win_size_px = win_size_px, 
        grid_size_px = grid_size_px, 
        area_of_interest= area_of_interest,
        verbosity=0)
    a = sidp.dic_parameters()
    b = expected_values_from_text_file()
    np.testing.assert_equal(list(a.values())[:4], b[0])
    np.testing.assert_equal(list(a.values())[4:], b[1])





#%%
if __name__ == "__main__":
    sidp = RollingImageMarkerTracker(
        reference_image=ref_img,
        win_size_px = win_size_px, 
        grid_size_px = grid_size_px, 
        area_of_interest= area_of_interest,
        verbosity=0)
    for k in range(2, 5):
        img = cv2.imread(str(test_images_dir/f"Cam_0000{k}.png"), cv2.IMREAD_GRAYSCALE)
        res = sidp.process_image(img)
        np.testing.assert_almost_equal(res['point_to_process'].flatten(), b[1+k], decimal=8)
        print(k)
    #%%

    #%%
    # read image series and write a separated result file 

    
    

# %%
