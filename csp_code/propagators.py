"""
This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
   """

def prop_BT(csp, newVar=None):
    """
    Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints
    """
    if not newVar:                  # if newVar is None:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:       # all variables are assigned
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    """
    Do forward checking. That is check constraints with
    only one uninstantiated variable. Remember to keep
    track of all pruned variable,value pairs and return
    """
    constraints = csp.get_cons_with_var(newVar) if newVar else csp.get_all_cons()
    pruned = []

    for constraint in constraints:
        if constraint.get_n_unasgn() != 1:
            continue                # skip to the next constraint

        # If we get here, get the single unassigned variable
        var = constraint.get_unasgn_vars()[0]
        for val in var.cur_domain():
            # Check if the var = val satisfies the constraint
            if not constraint.has_support(var, val):
                if (var, val) not in pruned:
                    # Then prune this value from var's domain
                    var.prune_value(val)
                    pruned.append((var, val))

        # After looking at all values in the var's domain, check if it is now empty
        if var.cur_domain_size() == 0:
            return False, pruned

    return True, pruned

def prop_GAC(csp, newVar=None):
    """
    Do GAC propagation. If newVar is None we do initial GAC enforce
    processing all constraints. Otherwise we do GAC enforce with
    constraints containing newVar on GAC Queue
    """
    constraints = csp.get_cons_with_var(newVar) if newVar else csp.get_all_cons()
    pruned = []

    # NOTE: although <constraints> is a list, the order is unimportant and acts like a set.
    # See page 209 of RN textbook
    while constraints != []:
        constraint = constraints.pop(0)     # grab the first constraint

        for var in constraint.get_unasgn_vars():        # get_scope()?
            for val in var.cur_domain():

                if not constraint.has_support(var, val):
                    # Check if we have already pruned (var, val)
                    if (var, val) not in pruned:
                        var.prune_value(val)
                        pruned.append((var, val))

                    # We have modified var's domain, so add back all constraints
                    # that have var in it's scope
                    for c in csp.get_cons_with_var(var):
                        if c not in constraints:
                            constraints.append(c)

            # Check if var's domain is empty
            if var.cur_domain_size() == 0:
                return False, pruned

    return True, pruned
