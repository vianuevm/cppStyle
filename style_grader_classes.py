class DefaultFilters(object):
    def __init__(self):
        self.goto = True
        self.globals = True
        self.breaks = True

#Todo: Define filters through command line arguments


class StyleError(object):
    """
    Represents a style error in the student's code.
    """

    def __init__(self):
        self.line_num = 0
        self.label = ""
        self.points_worth = 0

    def __init__(self, points, label, line_num):
        """
        Log the line number, type and point value of a specific error.
        points (int): Weight of this error.
        label (str): Key for response lookup in list_of_errors.
        line_num (int): Line number of this error.
        """

        list_of_errors = {
            "OPERATOR_SPACE_ERROR": "Incorrect spacing around operators",
            "INDENTATION_ERROR": "Incorrect indentation. Check to make sure you are four spaces in from previous code block.",
            "COMMAND_ERROR": "There should only be one command (statement) on each line.",
            "IF_ELSE_ERROR": "Every If-Else statement should have brackets.",
            "GLOBAL_VARIABLE": "You should never have a non-const global variable.",
            "FUNCTION_LENGTH_ERROR": "Your function is too long. Break it up into separate functions.",
            "LINE_WIDTH": "Line limit of 80 characters exceeded.",
            "BOOL_VALUE": "You need to return true or false, instead of an actual number.",
            "MAGIC_NUMBER": "Store numbers in variables, so that you can give them meaningful names.",
            "BRACES_ERROR": "Your braces should be either Egyptian or block style, pick one.",
            "SPACING_ERROR": "Use tabs or spaces, not both.",
            "UNNECESSARY_BREAK": "Breaks should ONLY be used in switch statements. Fix your logic.",
            "GOTO": "Never use the goto function.",
            "DEFINE_STATEMENT": "While define statements have their applications, we do not allow them in EECS 183.",
            "EQUALS_TRUE": "It is stylistically preferred to use 'if (x)' instead of 'if (x == true)'.",
            "WHILE_TRUE": "It is almost always preferred to use an explicit conditional instead of 'while(true)'.",
            "TERNARY_OPERATOR": "The use of ternary expressions (e.g. return f(x) ? true : false) is discouraged in EECS 183.",
            "CONTINUE_STATEMENT": "While 'continue' is occasionally appropriate, we discourage its use in EECS 183.",
            "MAIN_SYNTAX": "Your declaration of main() does not adhere to conventional stylistic guidelines.",
        }

        self.set_points_worth(points)
        self.set_line_num(line_num)
        self.set_label(list_of_errors[label])
        print list_of_errors[label]

    def set_line_num(self, line):
        self.line_num = line
    def set_label(self, label_name):
        self.label = label_name
    def set_points_worth(self, points):
        self.points_worth = points
    def get_points(self):
        return self.points_worth
    def get_label(self):
        return self.label
    def get_line_number(self):
        return self.line_num


class DataStructureTracker(object):
    """
    Counter object to track braces so we know whether or not we're inside a code block.
    """

    def __init__(self):
        self.in_block = False
        self.brace_stack = []
        self.brace_index = 1
        self.length_so_far = 0

    def get_length(self):
        return self.length_so_far

    def set_is_in_block(self, boolVar):
        self.in_block = boolVar

    def check_is_in_block(self):
        return self.in_block

    def add_brace(self, brace):
        self.brace_stack.append(brace)
        self.brace_index += 1

    def pop_brace(self):
        self.brace_stack.pop()
        self.brace_index -= 1
        if self.brace_index == 0:
            self.set_is_in_block(False)

    def get_brace_index(self):
        return self.brace_index


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
