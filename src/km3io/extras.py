#!/usr/bin/env python3


def scipy():
    """Imports and returns ``scipy``."""
    try:
        import scipy
    except ImportError:
        raise ImportError(
            "install the 'scipy' package with:\n\n"
            "    pip install pandas\n\n"
            "or\n\n"
            "    conda install scipy"
        )
    else:
        return scipy
