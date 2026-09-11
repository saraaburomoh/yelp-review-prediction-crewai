import numpy as np

def target_function(x, y):
    """
    The mathematical function to be minimized:
    f(x, y) = sin(x) * cos(y) + sin(x*y) + (x^2 + y^2) / 20
    
    Search Space: x, y in [-5, 5]
    Global Minimum: f(-1.704, 0.678) ≈ -1.5190
    """
    return np.sin(x) * np.cos(y) + np.sin(x * y) + (x**2 + y**2) / 20
