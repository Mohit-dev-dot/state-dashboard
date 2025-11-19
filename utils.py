import numpy as np
from scipy.stats import linregress

def safe_corr(s1, s2):
    try:
        return float(s1.corr(s2))
    except:
        return float('nan')

def safe_linreg(x, y):
    try:
        xr = np.asarray(x).astype(float)
        yr = np.asarray(y).astype(float)
        mask = np.isfinite(xr) & np.isfinite(yr)
        if mask.sum() < 2:
            return None
        return linregress(xr[mask], yr[mask])
    except:
        return None
