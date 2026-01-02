import numpy as np
import pytest

from py3dic.dic import DICGrid
from py3dic.dic.core.dic_result_loader import DICResultFileContainer
from py3dic.dic.core.core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement
from py3dic.dic.core.grid_size import GridSize

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



def test_dic_result_file_container(dic_result_file_container_fixture):
    # assert dic_result_file_container_fixture.no_frames == 4
    assert dic_result_file_container_fixture.xmin == 310.0
    assert dic_result_file_container_fixture.xmax == 370.0
    assert dic_result_file_container_fixture.xnum == 3
    assert dic_result_file_container_fixture.x_window_size == 90
    assert dic_result_file_container_fixture.ymin == 125.0
    assert dic_result_file_container_fixture.ymax == 185.0
    assert dic_result_file_container_fixture.ynum == 3
    assert dic_result_file_container_fixture.y_window_size == 90
    assert dic_result_file_container_fixture.imagelist[0] == 'Cam_00001.png'
    assert dic_result_file_container_fixture.imagelist[1] == 'Cam_00002.png'
    assert dic_result_file_container_fixture.imagelist[2] == 'Cam_00003.png'
    assert dic_result_file_container_fixture.imagelist[3] == 'Cam_00004.png'
    assert dic_result_file_container_fixture.pointlist[0].shape == (9, 2)
    assert dic_result_file_container_fixture.pointlist[1].shape == (9, 2)
    assert dic_result_file_container_fixture.pointlist[2].shape == (9, 2)
    assert dic_result_file_container_fixture.pointlist[3].shape == (9, 2)


def test_DIC_GRID(dic_result_file_container_fixture):
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
    i = -1
    mygrid:DICGrid = grid_list[i]
    assert isinstance(mygrid, DICGrid)
    mygrid.process_grid_data(
        reference_image=image_list[0], 
        image=image_list[i], 
        reference_points=point_list[0], 
        current_points=point_list[i], 
        interpolation_method=interpolation, 
        strain_type=strain_type, 
        remove_rigid_transform=rm_rigid_body_transform
    )



    # # self.winsize = winsize
    # parameter = "winsize"
    # expected = (90, 90)
    # np.testing.assert_allclose(mygrid.winsize, expected,rtol=1e-5, atol=1e-5)

    parameter = "reference_image"
    expected = 'Cam_00001.png'
    assert mygrid.reference_image == expected

    parameter = "image"
    expected ='Cam_00004.png'
    assert mygrid.image == expected

    parameter = "disp"
    expected = [(-2.4072876, 0.032577515), (-2.9313965, -1.2674103), (-1.5014648, -2.0356903), (-5.364502, 0.3045807), (-1.7254944, -0.16412354), (-1.6682129, -0.7373352), (4.7734375, 1.960556), (3.5157776, 1.1108551), (7.3092957, 0.79600525)]
    np.testing.assert_allclose(mygrid.disp, expected,rtol=1e-5, atol=1e-5)


    parameter = "correlated_point"
    expected = [[286.45355 , 121.862854],
       [285.9082  , 150.56247 ],
       [287.31647 , 179.79524 ],
       [313.49612 , 122.15488 ],
       [317.11325 , 151.68886 ],
       [317.14874 , 181.11569 ],
       [353.6328  , 123.840576],
       [352.35358 , 152.98993 ],
       [356.1251  , 182.6779  ]]
    np.testing.assert_allclose(mygrid.correlated_point, expected,rtol=1e-5, atol=1e-5)

    parameter = "reference_point"
    expected = [[310., 125.],
       [310., 155.],
       [310., 185.],
       [340., 125.],
       [340., 155.],
       [340., 185.],
       [370., 125.],
       [370., 155.],
       [370., 185.]]
    np.testing.assert_allclose(mygrid.reference_point, expected,rtol=1e-5, atol=1e-5)


