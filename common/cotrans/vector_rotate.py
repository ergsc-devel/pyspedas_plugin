import numpy as np

def vector_rotate( x0, y0, z0, nx, ny, nz, theta, x1, y1, z1):

    # Prepare sin\cos values for the rotation angle theta.
    dtor = np.pi / 180. # deg --> rad
    the = theta * dtor
    costhe = np.cos(the)
    sinthe = np.sin(the)

    #Normalize the rotation axis vector to the unit vector
    n = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= n
    ny /= n
    nz /= n
