
import pytest
import numpy as np
from py3dic.dic.core import DICGrid
from py3dic.dic.core.grid_size import GridSize

from py3dic.dic.core import DICResultFileContainer

@pytest.fixture(scope='module')
def result_dic_file_content_fixture():
    expected_lines =[]
    expected_lines.append('310.0	370.0	3	90\n')
    expected_lines.append('125.0	185.0	3	90\n')
    expected_lines.append('Cam_00001.png	310.0,125.0	310.0,155.0	310.0,185.0	340.0,125.0	340.0,155.0	340.0,185.0	370.0,125.0	370.0,155.0	370.0,185.0	\n')
    expected_lines.append('Cam_00002.png	298.3341,122.18497	298.3723,152.15681	298.4278,182.1235	328.31256,122.13837	328.93542,152.09497	331.95428,181.95987	366.49072,122.33831	366.2348,152.12717	367.20053,182.06662	\n')
    expected_lines.append('Cam_00003.png	294.31274,120.31217	294.36188,150.2475	294.4289,180.19241	324.32007,120.28953	324.9439,150.20859	327.96042,180.04742	362.5801,120.57312	362.30026,150.29019	363.25345,180.2068	\n')
    expected_lines.append('Cam_00004.png	286.45355,121.862854	285.9082,150.56247	287.31647,179.79524	313.49612,122.15488	317.11325,151.68886	317.14874,181.11569	353.6328,123.840576	352.35358,152.98993	356.1251,182.6779	\n')
    expected_lines.append('')
    return expected_lines

@pytest.fixture(scope='module')
def dic_result_file_container_fixture(result_dic_file_content_fixture):
    dic_result_file_container = DICResultFileContainer.from_lines(result_dic_file_content_fixture)
    return dic_result_file_container



@pytest.fixture
def artificial_dic_grid_factory():
    """ creates an dic grid with artificial displacement field
    
    """
    def _create_dic_grid(t:float):
        gs = GridSize(xmin=0, xmax=1, ymin=0, ymax=1, xnum=11, ynum=11, win_size_x=20, win_size_y=20)
        gs.prepare_gridXY()
        
        time_factor = 0.1
        disp_x = np.log(time_factor * t + 1) * np.log10(gs.grid_x * gs.grid_y + 1) * np.sqrt(gs.grid_x * gs.grid_y) * np.arctan2(gs.grid_x, gs.grid_y)
        disp_y = np.log(time_factor * t + 1) * np.log(gs.grid_x * gs.grid_y + 1) * np.sqrt(gs.grid_x * gs.grid_y) * np.arctan2(gs.grid_y, gs.grid_x)

        gr = DICGrid.from_gridsize(gs)
        gr.disp = np.column_stack([disp_x.ravel(), disp_y.ravel()])
        
        return gr
    
    return _create_dic_grid


@pytest.fixture
def grid_list_fixture(dic_result_file_container_fixture):
    # read/parse dic result file
    point_list = dic_result_file_container_fixture.pointlist
    image_list = dic_result_file_container_fixture.imagelist
    win_size = dic_result_file_container_fixture.get_winsize()
    grid_list = []
    disp_list = []
    # prepare Gridlist
    for i in range(len(image_list)):
        dic_gr = DICGrid.from_gridsize(dic_result_file_container_fixture.gs)
        grid_list.append(dic_gr)
    rm_rigid_body_transform = True
    interpolation = 'linear'
    strain_type = 'green_lagrange'
    for i, mygrid in enumerate(grid_list):
        mygrid.process_grid_data(
            win_size= win_size,
            reference_image=image_list[0], 
            image=image_list[i], 
            reference_points=point_list[0], 
            current_points=point_list[i], 
            interpolation_method=interpolation, 
            strain_type=strain_type, 
            remove_rigid_transform=rm_rigid_body_transform
        )
    return grid_list