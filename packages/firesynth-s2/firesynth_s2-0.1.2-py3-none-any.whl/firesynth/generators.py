import numpy as np
import pandas as pd
import random

from .config import HEALTHY_PRIORS, STRESSED_PRIORS, S2_TILES
from .utils import bounded_normal, random_dates
from .indices import ndvi, ndwi, nbr


class FireSynthS2:
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)

    def _generate_class(self, n, priors, label):
        data = {
            "S2_tile": np.random.choice(S2_TILES, n),
            "acquisition_date": random_dates(n)
        }

        for band, (mean, std) in priors.items():
            data[band] = bounded_normal(mean, std, n)

        df = pd.DataFrame(data)
        df["label"] = label
        return df


    def generate(self, n_per_class=8000, include_indices=True):
        
        healthy = self._generate_class(n_per_class, HEALTHY_PRIORS, 0)
        stressed = self._generate_class(n_per_class, STRESSED_PRIORS, 1)

        df = pd.concat([healthy, stressed], ignore_index=True)

        if include_indices:
            df["NDVI"] = ndvi(df["B08_nir"], df["B04_red"])
            df["NDWI"] = ndwi(df["B08_nir"], df["B11_swir1"])
            df["NBR"]  = nbr(df["B08_nir"], df["B12_swir2"])

        return df.sample(frac=1).reset_index(drop=True)
