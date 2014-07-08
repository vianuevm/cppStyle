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
            self.in_block = False

    def pop_switch_brace(self):
        self.switch_brace_stack.pop()
        self.switch_brace_index -= 1
        if self.switch_brace_index == 0:
            self.in_switch = False
