import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.optimize import brentq

def dist_moments(pdf, cdf, support=(0, np.inf), params=()):
    mean_val, _ = quad(lambda x: x * pdf(x, *params), *support)
    var_val, _ = quad(lambda x: (x-mean_val)**2 * pdf(x, *params), *support)

    skew_num, _ = quad(lambda x: (x-mean_val)**3 * pdf(x, *params), *support)
    skew_val = skew_num / var_val**1.5

    kurt_num, _ = quad(lambda x: (x-mean_val)**4 * pdf(x, *params), *support)
    kurt_val = kurt_num / var_val**2

    lo, hi = support
    if np.isinf(hi):
        hi = 1
        while cdf(hi, *params) < 0.999:
            hi *= 2

    median = brentq(lambda q: cdf(q, *params)-0.5, lo, hi)

    grid = np.linspace(lo, hi, 600)
    mode = grid[np.argmax([pdf(x, *params) for x in grid])]

    return pd.DataFrame({
        "Mean": [mean_val],
        "Variance": [var_val],
        "Skewness": [skew_val],
        "Kurtosis": [kurt_val],
        "Median": [median],
        "Mode": [mode]
    })