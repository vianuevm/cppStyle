class DefaultFilters(object):
    def __init__(self):
        self.goto = True
        self.globals = True
        self.breaks = True

#Todo: Define filters through command line arguments


class SpacingTracker(object):
    """
    Just a set of booleans to track spacing, modular in case this gets expanded.
    """
    def __init__(self):
        self.asts_left = False
        self.asts_right = False
        self.amps_left = False
        self.amps_right = False
        self.amps_both = False

class DataStructureTracker(object):
    """
    Counter object to track braces so we know whether or not we're inside a code block.
    """

    def __init__(self):
        self.in_block = False
        self.brace_stack = []
        self.brace_index = 1
        self.switch_brace_index = 0
        self.length_so_far = 0
        self.in_switch = False
        self.switch_brace_stack = []

    def get_length(self):
        return self.length_so_far

    def set_is_in_block(self, bool_var):
        self.in_block = bool_var

    def check_is_in_block(self):
        return self.in_block

    def add_switch_brace(self, brace):
        self.switch_brace_stack.append(brace)
        self.switch_brace_index += 1

    def add_brace(self, brace):
        self.brace_stack.append(brace)
        self.brace_index += 1

    def pop_brace(self):
        self.brace_stack.pop()
        self.brace_index -= 1
        if self.brace_index == 0:
            self.set_is_in_block(False)

    def pop_switch_brace(self):
        self.switch_brace_stack.pop()
        self.switch_brace_index -= 1
        if self.switch_brace_index == 0:
            self.set_in_switch(False)

    def get_brace_index(self):
        return self.brace_index

    def set_in_switch(self, truth_val):
        self.in_switch = truth_val


    def is_in_switch(self):
        return self.in_switch

class OperatorSpace(object):
    """
    Counter object to track instances of binary operands.
    """
    
    def __init__(self):
        self.add = 0
        self.sub = 0
        self.greater = 0
        self.less = 0
        self.divide = 0
        self.mod = 0
        self.total = 0 #TODO: Only calculate total on request

    def add_even_instance(self, amount): # Why is this named 'even'?
        self.add += amount
        self.total += amount

    def add_subtract_instance(self, amount):
        self.sub += amount
        self.total += amount

    def add_greater_than_instance(self, amount):
        self.greater += amount
        self.total += amount

    def add_less_than_instance(self, amount):
        self.less += amount
        self.total += amount

    def add_divide_instance(self, amount):
        self.divide += amount
        self.total += amount

    def add_mod_instance(self, amount):
        self.mod += amount
        self.total += amount
