#%%
from pathlib import Path
import cv2
import numpy as np
import pytest
from py3dic.dic import BatchImageMarkerTracker, BatchDICStrainProcessor
from py3dic.dic._obsolete._old_pydic import read_dic_file

def expected_output_from_text_file():
    """This is a function that returns the text

    Returns:
        _type_: _description_
    """    
    expected_list =[]
    expected_list.append('310.0	370.0	3	90\n')
    expected_list.append('125.0	185.0	3	90\n')
    expected_list.append('Cam_00001.png	310.0,125.0	310.0,155.0	310.0,185.0	340.0,125.0	340.0,155.0	340.0,185.0	370.0,125.0	370.0,155.0	370.0,185.0	\n')
    expected_list.append('Cam_00002.png	298.3341,122.18497	298.3723,152.15681	298.4278,182.1235	328.31256,122.13837	328.93542,152.09497	331.95428,181.95987	366.49072,122.33831	366.2348,152.12717	367.20053,182.06662	\n')
    expected_list.append('Cam_00003.png	294.31274,120.31217	294.36188,150.2475	294.4289,180.19241	324.32007,120.28953	324.9439,150.20859	327.96042,180.04742	362.5801,120.57312	362.30026,150.29019	363.25345,180.2068	\n')
    expected_list.append('Cam_00004.png	286.45355,121.862854	285.9082,150.56247	287.31647,179.79524	313.49612,122.15488	317.11325,151.68886	317.14874,181.11569	353.6328,123.840576	352.35358,152.98993	356.1251,182.6779	\n')

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



def test_batch_dic_processor(tmp_path):
    current_file_dir = Path(__file__).resolve().parent
    test_images_dir = current_file_dir / "example_imgs"
    image_pattern = str(test_images_dir / "*.png")

    win_size_px = (90, 90)
    grid_size_px = (30, 30)
    result_file = tmp_path/"test_results.txt"
    area_of_interest = ((310, 125), (371, 191))

    idp  = BatchImageMarkerTracker(image_pattern=image_pattern, 
                                      win_size_px=win_size_px, 
                                      grid_size_px=grid_size_px, 
                                      result_file=result_file, 
                                      area_of_interest=area_of_interest, 
                                      verbosity=0)
    idp.compute_and_save_results()

    dicp = BatchDICStrainProcessor(
        result_file = result_file, 
            interpolation='raw', 
            save_image=False, 
            scale_disp=4., scale_grid=25., 
            strain_type='green_lagrange', 
            rm_rigid_body_transform=True, 
            meta_info_file=None,
            unit_test_mode = True)
    dicp.process_data()

    grid_listres = read_dic_file(
        result_file = result_file, 
            interpolation='raw', 
            save_image=False, 
            scale_disp=4., scale_grid=25., 
            strain_type='green_lagrange', 
            rm_rigid_body_transform=True, 
            meta_info_file=None,
            unit_test_mode = True)

    assert (result_file).exists(), "Results file not created"

    for k in range(4):
        a = dicp.grid_list[k]
        b = grid_listres[k] 
        np.testing.assert_equal(a.strain_xx, b.strain_xx)
        np.testing.assert_equal(a.strain_yy, b.strain_yy)
        np.testing.assert_equal(a.strain_xy, b.strain_xy)
        np.testing.assert_equal(a.disp, b.disp)
        np.testing.assert_equal(a.disp_x, b.disp_x)
        np.testing.assert_equal(a.disp_y, b.disp_y)


    # Clean up the test results file
    if result_file.exists():
        result_file.unlink()





#%%
# This section is for helping with the developement of the tests.
# it immitates the environment of the pytest test
if __name__ == "__main__":
    pass
    current_file_dir = Path(__file__).resolve().parent
    test_images_dir = current_file_dir / "example_imgs"
    image_pattern = str(test_images_dir / "*.png")

    win_size_px = (90, 90)
    grid_size_px = (30, 30)
    result_file = current_file_dir/"test_results.txt"
    area_of_interest = ((310, 125), (371, 191))

    idp  = BatchImageMarkerTracker(image_pattern=image_pattern, 
                                      win_size_px=win_size_px, 
                                      grid_size_px=grid_size_px, 
                                      result_file=result_file, 
                                      area_of_interest=area_of_interest, 
                                      verbosity=0)
    idp.compute_and_save_results()

    dicp = BatchDICStrainProcessor(
        result_file = result_file, 
            interpolation='raw', 
            save_image=False, 
            scale_disp=4., scale_grid=25., 
            strain_type='green_lagrange', 
            rm_rigid_body_transform=True, 
            meta_info_file=None,
            unit_test_mode = True)
    dicp.process_data()
    grid_listres = read_dic_file(
        result_file = result_file, 
            interpolation='raw', 
            save_image=False, 
            scale_disp=4., scale_grid=25., 
            strain_type='green_lagrange', 
            rm_rigid_body_transform=True, 
            meta_info_file=None,
            unit_test_mode = True)
    
# %%
