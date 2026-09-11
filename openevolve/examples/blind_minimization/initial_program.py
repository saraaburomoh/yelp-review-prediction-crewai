"""
Blind Function Minimization — initial seed program.

This version uses a naive random search as the starting point.
OpenEvolve will evolve the EVOLVE-BLOCK to discover smarter strategies.

Key difference from the regular function_minimization example:
  - The evaluator does NOT know the true global minimum coordinates.
  - Scoring is purely relative: improvement over the current population best.
  - The target function is defined OUTSIDE the evolve block so the LLM
    can be told to optimize for ANY user-defined function.
"""
import numpy as np

# =====================================================================
# TARGET FUNCTION — defined here so users can swap it freely.
# The EVOLVE-BLOCK below must NOT hardcode assumptions about this function.
# =====================================================================
def target_function(x, y):
    """
    The function we want to minimize.
    Users can replace this with any 2D function they like.

    Default: a multi-modal landscape with many local minima.
      f(x, y) = sin(x)*cos(y) + sin(x*y) + (x^2 + y^2) / 20
    Search space: x, y in [-5, 5]
    """
    return np.sin(x) * np.cos(y) + np.sin(x * y) + (x**2 + y**2) / 20


# =====================================================================
# EVOLVE-BLOCK — OpenEvolve will mutate ONLY the code inside this block.
# =====================================================================
# EVOLVE-BLOCK-START
def search_algorithm(func, bounds=(-5, 5), iterations=1000):
    """
    Naive random search — the seed algorithm.
    OpenEvolve will replace this with smarter strategies.

    Args:
        func:       The function to minimize. Call it as func(x, y).
        bounds:     (min, max) search boundary for both x and y.
        iterations: Maximum number of function evaluations allowed.

    Returns:
        Tuple (best_x, best_y, best_value)
    """
    best_x = np.random.uniform(bounds[0], bounds[1])
    best_y = np.random.uniform(bounds[0], bounds[1])
    best_value = func(best_x, best_y)

    for _ in range(iterations):
        x = np.random.uniform(bounds[0], bounds[1])
        y = np.random.uniform(bounds[0], bounds[1])
        value = func(x, y)

        if value < best_value:
            best_value = value
            best_x, best_y = x, y

    return best_x, best_y, best_value
# EVOLVE-BLOCK-END


# =====================================================================
# Entry point — evaluator calls run_search(); must stay outside the block.
# =====================================================================
def run_search():
    """Run the search on the target function and return results."""
    x, y, value = search_algorithm(func=target_function, bounds=(-5, 5), iterations=1000)
    return x, y, value


if __name__ == "__main__":
    x, y, value = run_search()
    print(f"Found minimum at x={x:.4f}, y={y:.4f} with value={value:.4f}")
