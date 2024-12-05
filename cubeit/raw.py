import numpy as np
import os

"""
Reorders the pixels in an input RAW image into a cube
"""
def raw2cube(raw, pattern, band_number=None):
    H,W = raw.shape
    h,w = H // pattern, W // pattern
    cube = raw.reshape(h, pattern, w, pattern).swapaxes(1, 2).reshape(h, w, -1)
    if band_number is not None:
        return cube[:,:,:band_number]
    return cube

def raw2cube_chw(raw, pattern, band_number=None):
    return np.moveaxis(raw2cube(raw, pattern, band_number),-1,0)

"""
Reverse demosaicing : turns a cube into a RAW image
"""
def low_res_raw_chw(cube, pattern):
    # create low res raw image
    c,h,w = cube.shape
    y,x = np.mgrid[0:h, 0:w]
    band_ind = (y % pattern) * pattern + x % pattern 
    band_ind = np.minimum(c - 1, band_ind)
    data_lr = cube[band_ind, y, x].reshape(h, w)
    return data_lr

def low_res_cube_chw(cube, pattern):
    data_lr = low_res_raw_chw(cube, pattern)
    cube_lr = raw2cube_chw(data_lr, pattern, cube.shape[-1])
    return cube_lr


"""
Read RAW frames into numpy array
@param filename: filename of input image
@param bitdepth: bitdepth of image (8, 16 or 32)
@param width: width of input image
@param height: height of input image
@return: floating point image data
"""
def read_raw(filename, bitdepth, width, height):
    options_bitdepth = {8 : np.uint8, 16 : np.uint16, 32 : np.uint32}

    with open(filename, 'rb') as fid:
        if os.stat(filename).st_size < (height*width*bitdepth/8):
            data = np.zeros(shape = (height, width))
        else:
            data = np.fromfile(fid, options_bitdepth[bitdepth]).reshape((height,width)).astype(float)

    return data

