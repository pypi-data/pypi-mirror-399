import sympy
from sympy import Matrix, Rational, sympify

def get_matrix_from_input():
    rows = []
    while True:
        try:
            line = input().strip()
            
            if not line:
                if not rows:
                    print("No matrix entered. Please try again.")
                    continue
                break
            

            row = []
            for element in line.split():
                try:
                    if '/' in element and '.' not in element:
                        row.append(Rational(element))
                    else:
                        row.append(sympify(element))
                except:
                    raise ValueError(f"Cannot parse '{element}'")
            
            if rows and len(row) != len(rows[0]):
                print(f"Error: Row has {len(row)} elements, expected {len(rows[0])}. Try again.")
                continue
                
            rows.append(row)
            
        except ValueError as e:
            print(f"Error: {e}. Please enter valid numbers (integers, decimals, or fractions like 1/2).")
            continue
        except EOFError:
            break
    
    if not rows:
        raise ValueError("No matrix provided")
    
    return Matrix(rows)

if __name__ == "__main__":
    get_matrix_from_input()