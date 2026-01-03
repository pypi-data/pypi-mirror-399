import argparse
from lincalg.input import get_matrix_from_input
from lincalg.operations.operations import (
    rref,
    ref,
    gram_schmidt,
    nullspace,
    column_space
)
#functions

OPERATIONS = {
    'gram-schmidt': gram_schmidt,
    'rref': rref,
    'ref': ref,
    'nullspace': nullspace,
    'column-space': column_space,
}

def main():
    parser = argparse.ArgumentParser(
        description="A simple CLI for linear algebra calculations.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
        Available operations:
        gram-schmidt    Gram-Schmidt orthogonalization
        rref            Reduced row echelon form
        ref             Row echelon form
        nullspace       Null space basis
        column-space    Column space basis

        Example:
        "linalg rref"
        (then enter your matrix with columns seperated by spaces and rows seperated by new lines)
        """
    )

    parser.add_argument(
        'operation',
        choices=OPERATIONS.keys(), #switch to OPERATIONS.keys() later
        help='Operation to perform'
    )

    args = parser.parse_args()

    print(f"\nPerforming: {args.operation}")
    print("Enter your matrix (space-separated values, press Enter for new row, empty line when done):")

    try:
        matrix = get_matrix_from_input()

        operation_func = OPERATIONS[args.operation]
        result = operation_func(matrix)

        print(f"\nResult:")
        print_result(result)
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    return 0

def print_result(result):
    from sympy import Matrix
    
    if isinstance(result, Matrix):
        for i in range(result.rows):
            row = result.row(i)
            row_str = ' '.join(str(elem) for elem in row)
            print(row_str)
    elif isinstance(result, list):
        if result and isinstance(result[0], Matrix):
            for i, vec in enumerate(result):
                print(f"\nVector {i+1}:")
                vector = []
                for i in range(vec.rows):
                    row = vec.row(i)
                    vector.append(' '.join(str(elem) for elem in row))
                vector_str = ' '.join(str(elem) for elem in vector)
                print(vector_str)
        else:
            print(result)
    else:
        print(result)
if __name__ == "__main__":
    exit(main())