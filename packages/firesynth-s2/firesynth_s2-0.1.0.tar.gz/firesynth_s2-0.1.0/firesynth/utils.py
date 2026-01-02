import numpy as np
from datetime import datetime, timedelta
import random

def bounded_normal(mean, std, n, low=0.0, high=1.0):
    x = np.random.normal(mean, std, n)
    return np.clip(x, low, high)

def random_dates(n, start="2023-06-01", end="2023-09-01"):
    start = datetime.fromisoformat(start)
    end = datetime.fromisoformat(end)
    d = (end - start).days
    return [(start + timedelta(days=random.randint(0, d))).date().isoformat() for _ in range(n)]
