import numpy as np

def vector_rotate( x0, y0, z0, nx, ny, nz, theta, x1, y1, z1):

    # Prepare sin\cos values for the rotation angle theta.
    dtor = np.pi / 180. # deg --> rad
    the = theta * dtor
    costhe = np.cos(the)
    sinthe = np.sin(the)
    x0_length = x0.shape[0]

    #Normalize the rotation axis vector to the unit vector
    n = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= n
    ny /= n
    nz /= n

    rodrigues_mat =  np.concatenate([
    np.array([ nx*nx*(1. -costhe) + costhe, nx*ny*(1. -costhe)-nz*sinthe, nz*nx*(1. -costhe)+ny*sinthe ]).T,
    np.array([ nx*ny*(1. -costhe)+nz*sinthe, ny*ny*(1. -costhe)+costhe, ny*nz*(1. -costhe)-nx*sinthe ]).T,
    np.array([nz*nx*(1. -costhe)-ny*sinthe, ny*nz*(1. -costhe)+nx*sinthe, nz*nz*(1. -costhe)+costhe ]).T 
    ],axis=1).reshape(x0_length,3,3)

    inputed_vector =np.concatenate([[x0,y0,z0]],axis=1).T
    rotated_vector = [np.dot(rodrigues_mat[i,:,:], inputed_vector[i,:]) for i in range(x0_length)]

    return rotated_vector