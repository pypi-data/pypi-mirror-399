#%%
import logging
logger = logging.getLogger(__name__)

import numpy as np 
from py3dic.dic.core.core_calcs import compute_displacement
from py3dic.dic.core import DICResultFileContainer

#%%
        
class ComputeDispAndRemoveRigidTransformArray:
    def __init__(self):
        pass

    def _get_ABN(self):
        """
        Returns matrices of points after removing rows where 'new_points' contains NaNs.
        Strictly asserts that if a row is removed, all coordinates 
        in both 'new' and 'old' points are NaNs.
        
        Returns:
        - A: new points (np.array)
        - B: old points (np.array)
        - N: the number of points in the new arrays
        """
        
        A = []
        B = []
        new_points = self.new_points
        old_points = self.old_points
        removed_indices = []
        for i in range(len(new_points)):
            if np.isnan(new_points[i][0]):
                assert (
                    np.isnan(new_points[i][0])
                    and np.isnan(new_points[i][1])
                    and np.isnan(old_points[i][0])
                    and np.isnan(old_points[i][1])
                )
                removed_indices.append(i)
            else:
                A.append(new_points[i])
                B.append(old_points[i])

        new_a = np.array(A, dtype=np.float64)
        old_b = np.array(B, dtype=np.float64)
        assert len(new_a) == len(old_b)
        N = new_a.shape[0]  # total points
        return new_a, old_b, N

    def _get_XX(self, X):
        """
        Returns centered point matrix XX.
        
        Returns:
        - XX: centered points (np.array)
        """
        centroid_X = np.mean(X, axis=0)
        XX = X - centroid_X
        return XX, centroid_X 

    def _calc_R(self, AA, BB):
        H = np.transpose(AA) @ BB
        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        # special reflection case
        if np.linalg.det(R) < 0:
            print("Reflection detected")
            Vt[2, :] *= -1
            R = Vt.T @ U.T
        return R

    def compute(self, new_points, old_points) -> np.array:
        """Computes the displacement between two point sets and removes rigid transform.

        This function computes the optimal rotation and translation between two sets of
        points (p1 and p2) using Singular Value Decomposition (SVD). The function also
        removes the rigid transform between the point sets and returns the displacement
        between them.

        Args:
            new_points (numpy.array): An Nx2 numpy array representing the first set of 2D points.
            old_points (numpy.array): An Nx2 numpy array representing the second set of 2D points.

        Returns:
            numpy.array: An Nx2 numpy array representing the displacement between the two
                            point sets after removing the rigid transform.

        Raises:
            AssertionError: If the lengths of the input point sets do not match.
        """
        # reinitialise the object
        self.new_points = np.array(new_points, dtype=np.float64)
        self.old_points = np.array(old_points, dtype=np.float64)
        self.A = None
        self.B = None
        self.removed_indices = None
        

        self.A, self.B, self.N = self._get_ABN()


        # AA, BB = self._get_AA_BB()
        AA, centroid_A = self._get_XX(self.A)
        BB, centroid_B = self._get_XX(self.B)

        self.R = self._calc_R(AA, BB)

        n = len(self.A)
        assert n == self.N, "Number of points in A and N do not match"
        
        # Ensure column vectors for geometry math
        cA = centroid_A.reshape(-1, 1)
        cB = centroid_B.reshape(-1, 1)

        T = -self.R @ cA + cB
        A2 = (self.R @ self.A.T) + np.tile(T, (1, n))
        A2 = np.array(A2.T)

        out = []
        j = 0
        for i in range(len(new_points)):
            if np.isnan(new_points[i][0]):
                out.append(new_points[i])
            else:
                out.append(A2[j])
                j = j + 1
        out = np.array(out, dtype=np.float64)
        return compute_displacement(np.array(old_points, dtype=np.float64), out)

#%%
#%%
if __name__ == "__main__":
    def result_dic_file_content_fixture():
        """this create a 4 image dataset.

        each image has a grid of 9 points (3x3)

        """

        expected_lines = []
        expected_lines.append("310.0	370.0	3	90\n")
        expected_lines.append("125.0	185.0	3	90\n")
        expected_lines.append(
            "Cam_00001.png	310.0,125.0	310.0,155.0	310.0,185.0	340.0,125.0	340.0,155.0	340.0,185.0	370.0,125.0	370.0,155.0	370.0,185.0	\n"
        )
        expected_lines.append(
            "Cam_00002.png	298.3341,122.18497	298.3723,152.15681	298.4278,182.1235	328.31256,122.13837	328.93542,152.09497	331.95428,181.95987	366.49072,122.33831	366.2348,152.12717	367.20053,182.06662	\n"
        )
        expected_lines.append(
            "Cam_00003.png	294.31274,120.31217	294.36188,150.2475	294.4289,180.19241	324.32007,120.28953	324.9439,150.20859	327.96042,180.04742	362.5801,120.57312	362.30026,150.29019	363.25345,180.2068	\n"
        )
        expected_lines.append(
            "Cam_00004.png	286.45355,121.862854	285.9082,150.56247	287.31647,179.79524	313.49612,122.15488	317.11325,151.68886	317.14874,181.11569	353.6328,123.840576	352.35358,152.98993	356.1251,182.6779	\n"
        )
        expected_lines.append("")
        return expected_lines

    dic_result_file_container = DICResultFileContainer.from_lines(
        result_dic_file_content_fixture()
    )


    point_list = dic_result_file_container.pointlist
    image_list = dic_result_file_container.imagelist

    a1 = (compute_disp_and_remove_rigid_transform(point_list[1], point_list[0]))
    cdr = ComputeDispAndRemoveRigidTransformArray()
    a2 = cdr.compute(point_list[1], point_list[0]) 
    print(a1-a2)
    
    
# %%
