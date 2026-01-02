import numpy as np
import pytest
from py3dic.dic.core.core_calcs import compute_displacement, remove_point_outside, compute_disp_and_remove_rigid_transform
from py3dic.dic.core.grid_size import GridSize

def test_compute_displacement():
    point = np.array([[1, 2], [3, 4], [5, 6]])
    pointf = np.array([[2, 3], [4, 5], [6, 7]])
    expected_result = [(1, 1), (1, 1), (1, 1)]
    result = compute_displacement(point, pointf)
    
    np.testing.assert_allclose(result,expected_result, atol=1e-14,rtol=1e-14)

    point = np.array([[1, 2], [3, 4], [5, 6]])
    pointf = np.array([[2, 4], [4, 6], [6, 8]])
    expected_result = [(1, 2), (1, 2), (1, 2)]
    result = compute_displacement(point, pointf)
    np.testing.assert_allclose(result,expected_result, atol=1e-14,rtol=1e-14)

    point = np.array([[1, 2], [3, 4], [5, 6]])
    pointf = np.array([[1, 2], [3, 4], [5, 6]])
    expected_result = [(0, 0), (0, 0), (0, 0)]
    result = compute_displacement(point, pointf)
    np.testing.assert_allclose(result,expected_result, atol=1e-14,rtol=1e-14)

    point = np.array([[1, 2]])
    pointf = np.array([[2, 3]])
    expected_result = [(1, 1)]
    result = compute_displacement(point, pointf)
    np.testing.assert_allclose(result,expected_result, atol=1e-14,rtol=1e-14)

    point = np.array([])
    pointf = np.array([])
    expected_result = []
    result = compute_displacement(point, pointf)
    np.testing.assert_allclose(result,expected_result, atol=1e-14,rtol=1e-14)

    point = np.array([[1, 2], [3, 4], [5, 6]])
    pointf = np.array([[2, 3], [4, 5]])
    with pytest.raises(AssertionError):
        compute_displacement(point, pointf)
        


def test_compute_displacement_ag():
    """ this is a test for the compute_displacement function using 
    an artificially (predictable) generated field)

    """
    gs = GridSize(xmin=0, xmax=1, ymin=0, ymax=1, xnum=11, ynum=11, win_size_x=20, win_size_y=20)
    gs.prepare_gridXY()
    # prepare displacement field
    for t in range(1, 5):
        t = 1
        time_factor = 0.1
        disp_x = np.log(time_factor *t+1)*np.log10(gs.grid_x * gs.grid_y + 1) * np.sqrt(gs.grid_x * gs.grid_y) * np.arctan2(gs.grid_x, gs.grid_y)
        disp_y = np.log(time_factor*t+1)*np.log(gs.grid_x * gs.grid_y + 1) * np.sqrt(gs.grid_x * gs.grid_y) * np.arctan2(gs.grid_y, gs.grid_x)

        disp_field_flat = GridSize.grid_to_flat_array(disp_x, disp_y)
        
        coordinates = np.column_stack([gs.grid_x.ravel(), gs.grid_y.ravel()])
        new_coordinates = coordinates + np.column_stack([disp_x.ravel(), disp_y.ravel()])

        # =============================================== 
        disp_flat_simple  = new_coordinates - coordinates

        disp_func  = compute_displacement(coordinates, new_coordinates)

        np.testing.assert_allclose(disp_field_flat, disp_flat_simple, atol=1e-14,rtol=1e-14)
        np.testing.assert_allclose(disp_field_flat, disp_func, atol=1e-14,rtol=1e-14)


def test_remove_point_outside():
    # Test case 1: Empty input
    # assert remove_point_outside([],[]) == []

    # Test case 2: Single point inside the boundary
    points = [(1, 1), (5, 5), (10, 10), (15, 15)]
    area= [(0, 0), (10, 10)]
    expected_result = np.array([[ 1,  1], [ 5,  5],  [10, 10]])
    actual = remove_point_outside(points, area)
    assert np.testing.assert_array_equal(actual, expected_result) is None, "test with single point inside the boundary"
    
    # Test case 3: Single point inside the boundary
    points = [(10, 10)]
    area= [(0, 0), (10, 10)]
    expected_result = [(10, 10) ]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with single point outside the boundary"
    
    # Test case 3b: Single point inside the boundary
    points = [(12, 12)]
    area= [(0, 0), (10, 10)]
    expected_result = [ ]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with single point outside the boundary"


    # # Test case 5: All points outside the boundary
    points = [(10, 10), (15, 15), (20, 20)]
    area= [(0, 0), (5, 5)]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with all points outside the boundary"	

    # # Test case 6: Points with negative coordinates
    points = [(-1, -1), (0, 0), (5, 5), (10, 10)]
    area= [(0, 0), (5, 5)]
    expected_result = [(0, 0), (5, 5)]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with points with negative coordinates"

    # # Test case 7: X inside, Y outside
    points = [(4, 10), (1, 1)]
    area= [(0, 0), (5, 5)]
    expected_result = [(1, 1)]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with X inside, Y outside failed"

    # # Test case 8: Y inside, X outside
    points = [(10, 4), (2, 4)]
    area= [(0, 0), (5, 5)]
    expected_result = [(2, 4)]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None, "test with Y inside, X outside failed"

    # # Test case 9: Points with decimal coordinates
    points = [(1.5, 1.5), (2.5, 2.5), (3.5, 3.5)]
    area= [(0, 0), (5, 5)]
    expected_result =  [(1.5, 1.5), (2.5, 2.5), (3.5, 3.5)]
    assert np.testing.assert_array_equal(remove_point_outside(points, area), expected_result)  is None,"test with points with decimal coordinates failed"








