#%%
import pytest
import numpy as np
from py3dic.dic.core.dic_grid import \
    GridSize, DICGrid

def test_winsize():
    grid_size = GridSize(xmin=0, xmax=10, xnum=11, win_size_x=10, 
            ymin=0, ymax=10, ynum=11, win_size_y=10)
    win_size = grid_size.get_winsize()
    assert win_size == (10, 10)

def test_prepare_gridXY_correct_shape():
    grid_size = GridSize(xmin=0, xmax=10, xnum=11, win_size_x=10, 
            ymin=0, ymax=10, ynum=21, win_size_y=10)
    grid_xy = grid_size.prepare_gridXY()
    assert grid_xy[0].shape == (11, 21)
    assert grid_xy[1].shape == (11, 21)

def test_prepare_gridXY_correct_values():
    grid_size = GridSize(xmin=0, xmax=10, xnum=11, win_size_x=10, 
            ymin=0, ymax=10, ynum=21, win_size_y=10)
    grid_xy = grid_size.prepare_gridXY()
    for i in range(10):
        for j in range(20):
            assert grid_xy[0][i, j] == i
            assert grid_xy[1][i, j] == j*0.5

def test_create_DIC_Grid_bard():
    grid_size = GridSize(xmin=0, xmax=10, xnum=11, win_size_x=10, 
            ymin=0, ymax=10, ynum=21, win_size_y=10)
    dic_grid:DICGrid = DICGrid.from_gridsize(grid_size)
    assert dic_grid.size_x  == 11
    assert dic_grid.size_y  == 21
    assert dic_grid.grid_x.shape == (11, 21)
    assert dic_grid.grid_y.shape == (11, 21)

def test_from_tuplesXY_bard():
    xtuple = (0, 10, 11, 10)
    ytuple = (0, 10, 21, 10)
    grid_size = GridSize.from_tuplesXY(xtuple, ytuple)
    grid_size.prepare_gridXY()
    assert grid_size.get_winsize() == (10, 10)
    assert grid_size.grid_x.shape == (11,21)
    assert grid_size.grid_y.shape == (11,21)


def test_gridsize_init():
    gs = GridSize(0, 10, 5, 2, 0, 10, 5, 2)
    assert gs.xmin == 0
    assert gs.xmax == 10
    assert gs.xnum == 5
    assert gs.win_size_x == 2
    assert gs.ymin == 0
    assert gs.ymax == 10
    assert gs.ynum == 5
    assert gs.win_size_y == 2

def test_winsize():
    gs = GridSize(0, 10, 5, 2, 0, 10, 5, 2)
    assert gs.get_winsize() == (2, 2)

def test_prepare_gridXY():
    gs = GridSize(0, 10, 5, 2, 0, 10, 5, 2)
    grid_x, grid_y = gs.prepare_gridXY()
    assert np.array_equal(grid_x, np.mgrid[0:10:5*1j, 0:10:5*1j][0])
    assert np.array_equal(grid_y, np.mgrid[0:10:5*1j, 0:10:5*1j][1])

@pytest.mark.parametrize("xtuple, ytuple", [((0, 10, 5, 2), (0, 10, 5, 2))])
def test_from_tuplesXY(xtuple, ytuple):
    gs = GridSize.from_tuplesXY(xtuple, ytuple)
    assert gs.xmin == xtuple[0]
    assert gs.xmax == xtuple[1]
    assert gs.xnum == xtuple[2]
    assert gs.win_size_x == xtuple[3]
    assert gs.ymin == ytuple[0]
    assert gs.ymax == ytuple[1]
    assert gs.ynum == ytuple[2]
    assert gs.win_size_y == ytuple[3]


def test_grid_size_from_lines(result_dic_file_content_fixture):
    gs = GridSize.from_lines_list(result_dic_file_content_fixture)
    assert gs.xmin == 310.0,"xmin is not correct"
    assert gs.xmax == 370.0
    assert gs.xnum == 3
    assert gs.win_size_x == 90
    assert gs.ymin == 125.0
    assert gs.ymax == 185.0
    assert gs.ynum == 3
    assert gs.win_size_y == 90
    assert gs.get_winsize() == (90, 90)
    grid_x, grid_y = gs.prepare_gridXY()
    assert np.array_equal(grid_x, np.mgrid[310.0:370.0:3*1j, 125.0:185.0:3*1j][0])
    assert np.array_equal(grid_y, np.mgrid[310.0:370.0:3*1j, 125.0:185.0:3*1j][1])


# As `create_DIC_Grid` depends on a `DIC_Grid` object which is not defined in your code snippet,
# I can't write a test for it. You may need to modify this test to fit your real situation.
def test_create_DIC_Grid():
    gs = GridSize(0, 10, 5, 2, 0, 10, 5, 2)
    dic_grid = DICGrid.from_gridsize(gs)
    assert isinstance(dic_grid, DICGrid)  # Assuming DIC_Grid is your class name.
    assert np.array_equal(dic_grid.grid_x, gs.grid_x)
    assert np.array_equal(dic_grid.grid_y, gs.grid_y)
    assert dic_grid.size_x == gs.xnum
    assert dic_grid.size_y == gs.ynum



def test_grid_to_flat_array():
    x_grid = np.array([[1, 2], [3, 4]])
    y_grid = np.array([[5, 6], [7, 8]])
    expected_output = np.array([[1, 5], [2, 6], [3, 7], [4, 8]])

    result = GridSize.grid_to_flat_array(x_grid, y_grid)
    assert np.array_equal(result, expected_output), "grid_to_flat_array did not produce the expected output."

def test_flat_array_to_grid():
    flat_array = np.array([[1, 5], [2, 6], [3, 7], [4, 8]])
    grid_shape = (2, 2)
    expected_x_grid = np.array([[1, 2], [3, 4]])
    expected_y_grid = np.array([[5, 6], [7, 8]])

    x_grid, y_grid = GridSize.flat_array_to_grid(flat_array, grid_shape)
    assert np.array_equal(x_grid, expected_x_grid), "flat_array_to_grid did not produce the expected x_grid."
    assert np.array_equal(y_grid, expected_y_grid), "flat_array_to_grid did not produce the expected y_grid."

def test_flat_array_to_grid_invalid_input():
    flat_array = np.array([[1, 5], [2, 6], [3, 7]])  # Invalid shape
    grid_shape = (2, 2)

    with pytest.raises(ValueError, match="flat_array must be a numpy array with shape \\(n, 2\\), where n = xnum \\* ynum."):
        GridSize.flat_array_to_grid(flat_array, grid_shape)

def test_round_trip_conversion():
    x_grid = np.random.rand(11, 11)
    y_grid = np.random.rand(11, 11)
    
    flat_array = GridSize.grid_to_flat_array(x_grid, y_grid)
    x_grid_new, y_grid_new = GridSize.flat_array_to_grid(flat_array, x_grid.shape)
    
    assert np.array_equal(x_grid, x_grid_new), "Round-trip conversion failed for x_grid."
    assert np.array_equal(y_grid, y_grid_new), "Round-trip conversion failed for y_grid."


if __name__ == '__main__':
    pytest.main()