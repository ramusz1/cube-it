import cv2
import numpy as np
from .raw import raw2cube_chw, low_res_cube_chw

def upscale_shift(im, scale, offset, interp='linear'):
    """
    Shift image with offset
    :param im: input image
    :param offset: translation shift
    :param interp: 'lanczos' or 'linear'
    :return: shifted image
    
    """
    interp = {"lanczos": cv2.INTER_LANCZOS4, "linear": cv2.INTER_LINEAR}[interp]
    rows, cols = im.shape
    M = np.float32([[scale, 0, offset[1]], [0, scale, offset[0]]])
    return cv2.warpAffine(im, M, (int(cols * scale), int(rows * scale)), interp, borderMode=cv2.BORDER_REFLECT)


def gf_reproj_err_minimizer_chw(cube, raw, radius=1, debug=False, blur_coef=True, interp='linear', pattern=4):
    # create 2 low res cubes
    im = raw2cube_chw(raw, pattern)
    guide = low_res_cube_chw(cube, pattern)
    
    # calculate a and b of the guided filter
    smooth = 1e-10 # no smoothing would be the goal 
    (rows, cols, channels) = guide.shape
    ksize = radius * 2 + 1
    ksize = (ksize, ksize)

    def blur(img, ksize):
        out = img.copy()
        for i in range(out.shape[0]):
            out[i] = cv2.blur(out[i], ksize)
        return out

    meanI = blur(guide, ksize)
    meanP = blur(im, ksize)
    corrI = blur(guide * guide, ksize)
    corrIp = blur(guide * im, ksize)
    varI = corrI - meanI * meanI
    covIp = corrIp - meanI * meanP

    a = covIp / (varI + smooth)
    a = np.clip(np.abs(a), 0.1, 10.0) * np.sign(a) # limits weird cases
    b = meanP - a * meanI

    if blur_coef:
        a = blur(a, ksize)
        b = blur(b, ksize)
    if debug:
        print("a\n", a)
        print("b\n", b)
    
    # upscale a and b to full resolution of cube    
    A = []
    B = []
    for i in range(pattern):
        for j in range(pattern):
            n = i * pattern + j
            A.append(upscale_shift(a[n], pattern, [i,j], interp=interp))
            B.append(upscale_shift(b[n], pattern, [i,j], interp=interp))
    A = np.stack(A, axis=0)
    B = np.stack(B, axis=0)
    # apply the a and b to input cube
    # return cube * A + B, covIp, varI
    return cube * A + B
