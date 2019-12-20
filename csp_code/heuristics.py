"""
This file will contain different variable ordering heuristics to be used within
bt_search.

var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.

val_ordering == a function with the following template
    val_ordering(csp,var)
        ==> returns [Value, Value, Value...]

    csp is a CSP object, var is a Variable object; the heuristic can use csp to access the constraints of the problem, and use var to access var's potential values.

    val_ordering returns a list of all var's potential values, ordered from best value choice to worst value choice according to the heuristic.

"""
import random


def ord_mrv(csp):
    """
    Return the variable with the minimum remaining value (MRV).
    """
    # ANCHOR: alt version 1
    # variables = csp.get_all_unasgn_vars()
    # dom_sizes = [var.cur_domain_size() for var in variables]
    # min_index = dom_sizes.index(min(dom_sizes))
    # return variables[min_index]

    # ANCHOR: even shorter version!
    # variables = csp.get_all_unasgn_vars()
    # func = lambda var: var.cur_domain_size()
    # return min(variables, key=func)

    # ANCHOR: original version.. readable
    variables = csp.get_all_unasgn_vars()
    min_var = variables[0]
    min_dom_size = float('inf')
    for var in variables:
        dom_size = var.cur_domain_size()      # get the variables domain size

        if dom_size < min_dom_size:
            min_var = var
            min_dom_size = dom_size

    return min_var


def val_lcv(csp, var):
    """
    Return the least constraining value.
    """
    # Get all the variables except the variable passed in to val_lcv
    variables = [v for v in csp.get_all_unasgn_vars() if v != var]
    value_map = dict()

    for value in var.cur_domain():
        var.assign(value)
        pruned = 0

        # Check the other variables
        for _var in variables:
            for _val in var.cur_domain():
                for constraint in csp.get_cons_with_var(_var):
                    if not constraint.has_support(_var, _val):
                        pruned += 1
                        break           # skip the other constraints

        value_map[value] = pruned
        var.unassign()

    # sort in assending order -> least constrained... to most constrained value
    return sorted(value_map, key=value_map.get)
