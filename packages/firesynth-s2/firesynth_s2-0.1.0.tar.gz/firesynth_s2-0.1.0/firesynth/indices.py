import numpy as np

def ndvi(nir, red):
    return np.clip((nir - red) / (nir + red), -1, 1)

def ndwi(nir, swir1):
    return np.clip((nir - swir1) / (nir + swir1), -1, 1)

def nbr(nir, swir2):
    return np.clip((nir - swir2) / (nir + swir2), -1, 1)
