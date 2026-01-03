import numpy as np
from scipy.interpolate import interp1d

_lookuptable = np.linspace(-np.pi, 0, 10001)
_sinc_values = np.sinc(_lookuptable / np.pi)

_interpolator = interp1d(
    x=_sinc_values,
    y=_lookuptable,
    kind='linear',
    bounds_error=False,
    fill_value=(-np.pi, 0)
)


def inv_sinc(x):
    """Inverse Sinc function.

    Args:
        x (float or np.ndarray): Normalized Amplitude (0.0 ~ 1.0)

    Returns:
        float or np.ndarray: Phase value (-pi ~ 0.0)
    """
    return _interpolator(x)