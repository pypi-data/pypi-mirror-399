# calc_strain_calculator.py
"""
This module provides functions to calculate strain.

"""
import numpy as np
from .grid_size import GridSize
# from scipy.linalg import logm

class StrainCalculator:
    """
    A class used to calculate strain in materials.

    """
    def __init__(self, grid_x:np.array, grid_y:np.array):
        """
        Constructs all the necessary attributes for the StrainCalculator object.

        Parameters
        ----------
        grid_x : np.array
            The x-coordinates of the grid points.
        grid_y : np.array
            The y-coordinates of the grid points.
        """
        self.grid_x = grid_x
        self.grid_y = grid_y 
        self.strain_xx = np.full_like(grid_x, np.nan)
        self.strain_xy = np.full_like(grid_x, np.nan)
        self.strain_yy = np.full_like(grid_x, np.nan)

    def _get_grid_dx_dy(self)->tuple[float, float]:
        """
        Get the spatial increments based on the initial grid positions (uniform grid).
        # TODO: implement non-uniform grid

        Returns
        -------
        tuple
            The spatial increments (dx, dy).
        """
        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]
        return dx, dy

    def compute_strain_field_cauchy(self, disp_x: np.array, disp_y: np.array) -> tuple[np.array, np.array, np.array]:
        """
        Compute the Infinitesimal (Cauchy) strain tensor field. 
        #TODO activate this function

        This assumes small deformations where second-order terms are negligible.

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain tensor components (epsilon_xx, epsilon_yy, epsilon_xy).
            Note: epsilon_xy is the tensor shear strain, not the engineering shear gamma.
        """
        dx, dy = self._get_grid_dx_dy()

        # Calculate gradients
        du_dx, du_dy = np.gradient(disp_x, dx, dy, edge_order=2)
        dv_dx, dv_dy = np.gradient(disp_y, dx, dy, edge_order=2)

        # Linear strain formulas (dropping non-linear terms)
        self.strain_xx = du_dx
        self.strain_yy = dv_dy
        self.strain_xy = 0.5 * (du_dy + dv_dx)

        return self.strain_xx, self.strain_yy, self.strain_xy


    def compute_strain_green_lagrange(self, disp_x: np.array, disp_y:np.array)->tuple[np.array, np.array, np.array]:
        """
        Compute strain field from displacement using numpy.

        Green-Lagrange Strain

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        dx, dy = self._get_grid_dx_dy()

        du_dx, du_dy = np.gradient(disp_x, dx, dy, edge_order=2)
        dv_dx, dv_dy = np.gradient(disp_y, dx, dy, edge_order=2)

        self.strain_xx = du_dx + 0.5 * (du_dx**2 + dv_dx**2)
        self.strain_yy = dv_dy + 0.5 * (du_dy**2 + dv_dy**2)
        # this is the shear strain e_xy (not the engineering shear strain $\gamma_{xy}$
        self.strain_xy = 0.5 * (du_dy + dv_dx + 
                du_dx * du_dy + 
                dv_dx * dv_dy)
        return self.strain_xx, self.strain_yy, self.strain_xy

    def compute_strain_field_DA(self, disp_x: np.array, disp_y:np.array):
        """
        Compute strain field from displacement field using a large strain method (2nd order).

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """
        dx, dy = self._get_grid_dx_dy()

        for i in range(self.grid_x.shape[0]):
            for j in range(self.grid_y.shape[1]):
                du_dx = 0.
                dv_dy = 0.
                du_dy = 0.
                dv_dx = 0.

                if i - 1 >= 0 and i + 1 < self.grid_x.shape[0]:
                    du1 = (disp_x[i + 1, j] - disp_x[i - 1, j]) / 2.
                    du_dx = du1 / dx
                    dv2 = (disp_y[i + 1, j] - disp_y[i - 1, j]) / 2.
                    dv_dx = dv2 / dx

                if j - 1 >= 0 and j + 1 < self.grid_y.shape[1]:
                    dv1 = (disp_y[i, j + 1] - disp_y[i, j - 1]) / 2.
                    dv_dy = dv1 / dy
                    du2 = (disp_x[i, j + 1] - disp_x[i, j - 1]) / 2.
                    du_dy = du2 / dy

                self.strain_xx[i, j] = du_dx + 0.5 * (du_dx ** 2 + dv_dx ** 2)
                self.strain_yy[i, j] = dv_dy + 0.5 * (du_dy ** 2 + dv_dy ** 2)
                self.strain_xy[i, j] = 0.5 * (du_dy + dv_dx + du_dx * du_dy + dv_dx * dv_dy)
        return self.strain_xx, self.strain_yy, self.strain_xy
    
    def compute_strain_field_log(self, disp_x: np.array, disp_y: np.array):
        """
        Vectorized computation of Hencky Strain (Logarithmic).
        this should be faster

        TODO: replace compute_strain_field_log with this
        """
        # 1. Retrieve Grid Spacings (assuming constant pitch)
        # Note: If your grid is not uniform, pass the full grid_x/grid_y arrays to gradient
        dx, dy = self._get_grid_dx_dy()

        # this is necessary to convevt from:
        #    ij indexing (DIC pipeline) --> xy indexing (Henkcy calculation)
        # TODO: see if this can be fixed
        disp_x = disp_x.T
        disp_y = disp_y.T
        
        # 2. Compute Gradients (Vectorized Finite Differences)
        # np.gradient returns [d/d(axis0), d/d(axis1)] -> [d/dy, d/dx]

        # Gradient of u (disp_x)
        grad_u = np.gradient(disp_x, dy, dx) # pass spacing: (axis0_spacing, axis1_spacing)
        du_dy = grad_u[0]  # axis 0 change
        du_dx = grad_u[1]  # axis 1 change

        # Gradient of v (disp_y)
        grad_v = np.gradient(disp_y, dy, dx)
        dv_dy = grad_v[0]
        dv_dx = grad_v[1]

        # 3. Construct the Deformation Gradient Tensor F (in memory as mxnx2x2)
        # F = [[1 + du/dx,  du/dy],
        #      [dv/dx,      1 + dv/dy]]
        
        m, n = disp_x.shape
        F = np.zeros((m, n, 2, 2))
        
        F[:, :, 0, 0] = 1.0 + du_dx
        F[:, :, 0, 1] = du_dy
        F[:, :, 1, 0] = dv_dx
        F[:, :, 1, 1] = 1.0 + dv_dy

        # 4. Compute Right Cauchy-Green Tensor C = F.T @ F
        # We swap the last two axes for transpose: (m,n,2,2) -> (m,n,2,2)
        F_T = np.transpose(F, axes=(0, 1, 3, 2))
        C = np.matmul(F_T, F)

        # 5. Compute Eigenvalues of C
        # for symmetric matrices, eigvalsh is faster and more stable
        eigvals = np.linalg.eigvalsh(C) # Returns shape (m, n, 2)
        
        # 6. Compute Logarithmic Strain Eigenvalues
        # E = 0.5 * ln(C)
        eps_eig = 0.5 * np.log(eigvals)

        # 7. Reconstruct the Strain Tensor (Optional) or just return components
        # If you need the full tensor E_ij projected back to xy basis:
        # This step is complex to vectorize without einsum. 
        # But usually, engineers just want the principal strains (eps_eig).
        
        # If you strictly need Exx, Eyy, Exy in the original basis, 
        # we must reconstruct: E = R * diag(eps) * R.T
        # where R are the eigenvectors of C. 
        
        # For now, let's map what your original code tried to do:
        # Your code returned Exx, Eyy, Exy (components of the tensor)
        # The 'logm' does the rotation automatically.
        
        # To replicate 'logm' behavior vectorized:
        vals, vecs = np.linalg.eigh(C) # vecs shape (m,n,2,2) columns are eigenvectors
        
        # Construct diagonal strain matrix
        strain_diag = np.zeros_like(C)
        strain_diag[:, :, 0, 0] = eps_eig[:, :, 0]
        strain_diag[:, :, 1, 1] = eps_eig[:, :, 1]
        
        # E = V * log(Lambda) * V.T
        # This rotates the principal strains back to the global XY frame
        E_tensor = np.matmul(vecs, np.matmul(strain_diag, np.transpose(vecs, axes=(0,1,3,2))))
        
        self.strain_xx = E_tensor[:, :, 0, 0]
        self.strain_yy = E_tensor[:, :, 1, 1]
        self.strain_xy = E_tensor[:, :, 0, 1] # or [1,0], it's symmetric

        return self.strain_xx, self.strain_yy, self.strain_xy

    def compute_F_deformation_gradient(self, disp_x: np.array, disp_y: np.array) -> tuple[np.array, np.array, np.array, np.array]:
            """
            Compute the Deformation Gradient Tensor F.

            F = I + grad(u)
            
            Parameters
            ----------
            disp_x, disp_y : np.array
                Displacement fields.

            Returns
            -------
            tuple
                (F11, F12, F21, F22) corresponding to [[F11, F12], [F21, F22]].
            """
            dx, dy = self._get_grid_dx_dy()

            # Compute gradients (nabla u)
            # indexing='ij' assumption: axis 0 is x, axis 1 is y
            du_dx, du_dy = np.gradient(disp_x, dx, dy, edge_order=2)
            dv_dx, dv_dy = np.gradient(disp_y, dx, dy, edge_order=2)

            # F = I + nabla u
            
            F11 = 1.0 + du_dx    # F11 = 1 + du/dx
            F12 = du_dy          # F12 = du/dy
            F21 = dv_dx          # F21 = dv/dx
            F22 = 1.0 + dv_dy    # F22 = 1 + dv/dy

            return F11, F12, F21, F22

    def compute_right_cauchy_tensor(self, disp_x: np.array, disp_y: np.array) -> tuple[np.array, np.array, np.array]:
        """
        Compute the Right Cauchy-Green Deformation Tensor C.

        C = F.T @ F
        
        Parameters
        ----------
        disp_x, disp_y : np.array
            Displacement fields.

        Returns
        -------
        tuple
            (C11, C22, C12). 
            Note: C is symmetric, so C21 == C12.
        """
        # 1. Get F components
        F11, F12, F21, F22 = self.compute_F_deformation_gradient(disp_x, disp_y)

        # 2. Compute C = F.T * F
        # Matrix Multiplication:
        # [F11  F21]   [F11  F12]   [C11  C12]
        # [F12  F22] * [F21  F22] = [C21  C22]
        
        # C11 = F11*F11 + F21*F21
        C11 = F11**2 + F21**2
        
        # C22 = F12*F12 + F22*F22
        C22 = F12**2 + F22**2
        
        # C12 = F11*F12 + F21*F22
        C12 = F11 * F12 + F21 * F22

        return C11, C22, C12

    def compute_strain(self, disp_x: np.array, disp_y:np.array, method:str='green_lagrange'):
        """
        Compute strain field based on the specified method.

        Parameters
        ----------
        disp_x : np.array
            Displacement field in the x-direction.
        disp_y : np.array
            Displacement field in the y-direction.
        method : str
            Method to compute strain ('green_lagrange','cauchy-eng', '2nd_order', or 'log'): Default is 'green_lagrange'.

        Returns
        -------
        tuple
            The strain fields (strain_xx, strain_yy, strain_xy).
        """

        if method == 'green_lagrange':
            strain_xx, strain_yy, strain_xy  = self.compute_strain_green_lagrange(disp_x, disp_y)
        elif method == 'cauchy-eng':
            strain_xx, strain_yy, strain_xy  = self.compute_strain_field_cauchy(disp_x, disp_y)
        elif method == '2nd_order':
            strain_xx, strain_yy, strain_xy= self.compute_strain_field_DA(disp_x, disp_y)
        elif method == 'log':
            strain_xx, strain_yy, strain_xy= self.compute_strain_field_log(disp_x, disp_y)
        else:
            raise ValueError("Please specify a correct strain_type: 'green_lagrange', 'cauchy-eng', '2nd_order' or 'log'")

        return strain_xx.copy(), strain_yy.copy(), strain_xy.copy()

    @classmethod
    def from_gridsize(cls, grid_size: GridSize):
        """
        Create a StrainCalculator object from a GridSize object.

        Parameters
        ----------
        grid_size : GridSize
            An instance of the GridSize class.

        Returns
        -------
        StrainCalculator
            A StrainCalculator object.
        """
        return cls(grid_size.grid_x, grid_size.grid_y)
        