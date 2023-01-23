import numpy as np
 
def Frobenius(matrix: np.ndarray):

    if not isinstance(matrix, np.ndarray):
        return None
    else:
        n = matrix.shape[0]- 1  
        frob = np.zeros(shape=(n, n))
        
        for i in range(n - 1):
            frob[i][i+1] = 1
            frob[-1] = -1*matrix[::-1][:-1]

        return frob