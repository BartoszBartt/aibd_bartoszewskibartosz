from forbenius import *
import pytest
import numpy as np

frob_test_data = [
    (np.array([4,2,3,4]), np.array([[0, 1, 0], [0, 0, 1], [-4,-3,-2]])),
    (np.array([10,12,3,4,5]), np.array([[0, 1, 0, 0], [0, 0, 1,0], [0, 0, 0, 1], [-5,-4,-3,-12]])),
    (np.array([1,2,3,4,-7,-3]), np.array([[0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0],[0, 0, 0, 0, 1], [3, 7, -4, -3,-2]])),
    ([1,2,3], None)
    ]

@pytest.mark.parametrize('sample_coeffs, matrix', frob_test_data)
def test_Frobenius_mtx(sample_coeffs, matrix):
    
    frob_result = Frobenius(sample_coeffs)
    
    if isinstance(matrix, np.ndarray):
        assert (matrix == frob_result).all()
    else:
        assert matrix == frob_result