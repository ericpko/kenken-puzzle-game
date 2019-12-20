"""
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary
      all-different constraints for both the row and column constraints.

3. kenken_csp_model (worth 20/100 marks)
    - A model built using your choice of (1) binary binary not-equal, or (2)
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

"""
from cspbase import *
from functools import reduce
import itertools as it


def binary_ne_grid(kenken_grid):
    """
    """
    # Get the dimentions of the grid
    n = kenken_grid[0][0]
    # Get the initial domain for each variable. Dom(X) = {1, ..., n}
    domain = [x for x in range(1, n + 1)]
    # Create a variable for each cell in the grid. (This is a nested for loop).
    # NOTE: each inner list is a row of variables.
    # Eg) [[11, 12, ..., 1n], ..., [n1, ..., nn]]
    variables = [[Variable(f'{row}{col}', domain) for col in range(1, n + 1)] for row in range(1, n + 1)]

    # Create the CSP model
    # csp_model = CSP("binary_ne_grid", [var for row in variables for var in row])
    csp_model = CSP("binary_ne_grid", list(it.chain.from_iterable(variables))) # flatten

    # Create a set of 2-permutations to represent the satisfying tuples
    # Eg) ((1, 2), (1, 3), ..., (1, n), (2, 1), (2, 3), ..., (2, n), ..., (n, 1), ..., (n, n-1))
    bne_tuples = set(tup for tup in it.permutations(range(1, n + 1), 2))

    # Add all the binary not equal constraints to the CSP model
    for row in range(n):
        for col in range(n):
            for i in range(n):
                if i == col:
                    continue
                # Add the row constraints.
                constraint = Constraint(f'Row: {row + 1}{col + 1} & {row + 1}{i + 1}', [variables[row][col], variables[row][i]])
                constraint.add_satisfying_tuples(bne_tuples)
                csp_model.add_constraint(constraint)

                # Add the column constraints. (We can swap row and col)
                constraint = Constraint(f'Col: {col + 1}{row + 1} & {i + 1}{row + 1}', [variables[col][row], variables[i][row]])
                constraint.add_satisfying_tuples(bne_tuples)
                csp_model.add_constraint(constraint)

    return csp_model, variables


def nary_ad_grid(kenken_grid):
    """
    """
    # Set up the same as binary_ne_grid function
    n = kenken_grid[0][0]
    domain = [x for x in range(1, n + 1)]
    variables = [[Variable(f'{row}{col}', domain) for col in range(1, n + 1)] for row in range(1, n + 1)]

    # Initialize the CSP model
    csp_model = CSP("nary_ad_grid", list(it.chain.from_iterable(variables)))

    # Get all the permutations of (1, ..., n)
    all_diff_tups = set(tup for tup in it.permutations(range(1, n + 1)))

    # Add the all diff constraints
    for i in range(n):
        # Add the row all diff constraints
        constraint = Constraint(f'Row: {i + 1}', variables[i])
        constraint.add_satisfying_tuples(all_diff_tups)
        csp_model.add_constraint(constraint)

        # Add the column all diff constraints
        constraint = Constraint(f'Col: {i + 1}', [row[i] for row in variables])
        constraint.add_satisfying_tuples(all_diff_tups)
        csp_model.add_constraint(constraint)


    return csp_model, variables


def kenken_csp_model(kenken_grid):
    """
    """
    n = kenken_grid[0][0]
    # csp_model, variables = nary_ad_grid(kenken_grid)
    csp_model, variables = binary_ne_grid(kenken_grid)
    csp_model.name = 'kenken_csp_model'

    for cage in kenken_grid[1:]:
        if (len(cage) == 2):
            cell, target = cage[0], cage[1]
            row, col = int(str(cell)[0]) - 1, int(str(cell)[1]) - 1

            constraint = Constraint(f'{cage}', [variables[row][col]])
            tuples = [[target]]

        else:
            # Find the variables in each cage to make the cage constraint
            cage_vars = []
            for cell in cage[:-2]:
                # Get the row and column number of the cell
                # NOTE we need to subtract 1 to get the true index
                row, col = int(str(cell)[0]) - 1, int(str(cell)[1]) - 1
                cage_vars.append(variables[row][col])

            # Make the constraint with the ordered variables
            constraint = Constraint(f'{cage}', cage_vars)


            # Get the tuples satisfying the cages. Note that we use the product
            # in this case since the cages can have repeating values.
            # NOTE: we do not need to check permutations for addition and
            # multiplication since they are commutative in the naturals AND
            # we will still get all permutations that satisfy the target
            # since permutations(tup) is a subset of product(tup)
            tuples = set()
            op = cage[-1]           # operation
            target = cage[-2]
            for tup in it.product(range(1, n + 1), repeat=len(cage[:-2])):
                # CASE 1: addition
                if op == 0:
                    if sum(tup) == target:
                        tuples.add(tup)

                # CASE 2: subtraction
                elif op == 1:
                    if reduce(lambda x, y: x - y, tup) == target:
                        for perm in it.permutations(tup):
                            if perm not in tuples:
                                tuples.add(perm)

                # CASE 3: division
                elif op == 2:
                    if reduce(lambda x, y: x // y, tup) == target:
                        for perm in it.permutations(tup):
                            if perm not in tuples:
                                tuples.add(perm)

                # CASE 4: multiplication
                elif op == 3:
                    if reduce(lambda x, y: x * y, tup) == target:
                        tuples.add(tup)


        # Add the satisfying tuples and the constraint to the CSP model
        constraint.add_satisfying_tuples(tuples)
        csp_model.add_constraint(constraint)

    return csp_model, variables
