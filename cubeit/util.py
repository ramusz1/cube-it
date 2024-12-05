import numpy as np
    
def normalize_percentile(x, p1, p2):
    p1,p2 = np.percentile(x, [p1,p2])
    return np.clip((x - p1) / (p2 - p1), 0, 1.0)

def cube2RGB_chw(cube, gamma=0.4, bands=None, vmax=1.0):
    c = cube.shape[0]
    if bands is None:
        bands = [c - 1, c // 2, 0]
    rgb = cube[bands]
    rgb = np.power(rgb / vmax, gamma) 
    for i in range(3):
        rgb[i] = normalize_percentile(rgb[i], 1, 99)
    return np.moveaxis((rgb * 255).astype(np.uint8), 0, 2)

