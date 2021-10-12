import numpy as np

def vector_rotate( x0, y0, z0, nx, ny, nz, theta):

    # Prepare sin\cos values for the rotation angle theta.
    dtor = np.pi / 180. # deg --> rad
    the = theta * dtor
    costhe = np.cos(the)
    sinthe = np.sin(the)
    if isinstance(x0, np.ndarray): # for array x0
        x0_length = x0.shape[0]
        concatenate_axis_x0 = 1
    else: # for vector x0 (single component)
        x0_length = 1
        concatenate_axis_x0 = 0
    
    if isinstance(nx, np.ndarray): # for array nx
        nx_length = nx.shape[0]
        concatenate_axis_n = 1
    else: # for vector nx (single component)
        nx_length = 1
        concatenate_axis_n = 0

    #Normalize the rotation axis vector to the unit vector
    n = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= n
    ny /= n
    nz /= n

    rodrigues_mat =  np.concatenate([
    np.array([ nx*nx*(1. -costhe) + costhe, nx*ny*(1. -costhe)-nz*sinthe, nz*nx*(1. -costhe)+ny*sinthe ]).T,
    np.array([ nx*ny*(1. -costhe)+nz*sinthe, ny*ny*(1. -costhe)+costhe, ny*nz*(1. -costhe)-nx*sinthe ]).T,
    np.array([nz*nx*(1. -costhe)-ny*sinthe, ny*nz*(1. -costhe)+nx*sinthe, nz*nz*(1. -costhe)+costhe ]).T 
    ],axis=concatenate_axis_n).reshape(nx_length,3,3)

    inputed_vector =np.concatenate([[x0,y0,z0]],axis=concatenate_axis_x0).T
    if x0_length > 1 and nx_length > 1: #For all of (x0, y0, z0), (nx, ny, nz), (and theta) given as arrays. 
        rotated_vector = np.array([np.dot(rodrigues_mat[i,:,:], inputed_vector[i,:]) for i in range(x0_length)])
    elif x0_length > 1 and nx_length == 1: # For (x0,y0,z0) given as an array with a vector nx and scalar theta.
        rotated_vector = np.dot(rodrigues_mat, inputed_vector.T).T.reshape(x0_length, 3)
    elif x0_length == 1 and nx_length == 1: #For (x0, y0, z0) and (nx,ny,nz) given as a single vector
        rotated_vector = np.dot(rodrigues_mat, inputed_vector).reshape(3)

    return rotated_vector