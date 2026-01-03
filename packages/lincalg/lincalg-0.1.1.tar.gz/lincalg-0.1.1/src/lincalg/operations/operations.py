from sympy import Matrix

def rref(matrix):
    rref_form, pivot_cols = matrix.rref()

    return rref_form

def ref(matrix):
    return matrix.echelon_form()

def gram_schmidt(matrix):
    return GramSchmidt(matrix, True) #normalized
def column_space(matrix):
    return matrix.columnspace()
def nullspace(matrix):
    return matrix.nullspace()