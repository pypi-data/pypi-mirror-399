from sympy import Matrix

def add_matrices(A: Matrix, B: Matrix) -> Matrix:
    """
    Adds two matrices A and B using sympy.
    """
    # Convert to sympy matrices if not already
    A = Matrix(A) if not isinstance(A, Matrix) else A
    B = Matrix(B) if not isinstance(B, Matrix) else B

    # Check dimensions
    if A.shape != B.shape:
        raise ValueError(
            "Matrices must have the same shape, "
            f"got {A.shape} and {B.shape}")

    return A + B
