#TODO: Find this data a non-global home
#This is global/hard-coded for now till it gets a database home.
list_of_errors = {}
list_of_errors["OPERATOR_SPACE_ERROR"] = \
    "Incorrect spacing around operators"
list_of_errors["INDENTATION_ERROR"] = \
    "Incorrect indentation.  Check to make sure you are four spaces in from previous code block."
list_of_errors["COMMAND_ERROR"] = \
    "There should only be one command (statement) on each line.  Ever."
list_of_errors["IF_ELSE_ERROR"] = \
    "Every If-Else statement should have brackets, regardless."
list_of_errors["GLOBAL_VARIABLE"] = \
    "You should never, ever, ever... wait for it... ever have a non-const global variable."
list_of_errors["FUNCTION_LENGTH_ERROR"] = \
    "Your function should not be this long.  Break it up into separate functions."
list_of_errors["LINE_WIDTH"] = \
    "You exceeded 80 chars on a line.  This needs to be reformatted."
list_of_errors["BOOL_VALUE"] = \
    "You need to return true or false.  Not an actual number."
list_of_errors["MAGIC_NUMBER"] = \
    "Every number should be stored in a variable, not used as a literal."
list_of_errors["BRACES_ERROR"] = \
    "Your braces should be egyption style or block style.  You have some kind of formatting error."
list_of_errors["SPACING_ERROR"] = \
    "Use tabs or spaces, not both."
list_of_errors["UNNECESSARY_BREAK"] = \
    "Breaks should ONLY be used in switch statements.  Fix your logic."
list_of_errors["GOTO"] = \
    "Never use the goto function."


class DefaultFilters():
    def __init__(self):
        self.goto = True
        self.globals = True
        self.breaks = True

#Todo: Define filters through command line arguments


class StyleError():
    def __init__(self):
        self.line_num = 0
        self.label = ""
        self.points_worth = 0

    def __init__(self, points, label, line_num):
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


class DataStructureTracker():
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

class OperatorSpace():
    def __init__(self):
        self.add = 0
        self.sub = 0
        self.greater = 0
        self.less = 0
        self.divide = 0
        self.mod = 0
        self.total = 0

    def add_even_instance(self, amount):
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



class StyleRubric(object):
    """ This class sets all variable aspects of grading (whitespace, gotos etc)
    """
    def __init__(self):
        self.total_errors = 0
        self.filters = DefaultFilters()
        self.error_types = {}
        self.error_tracker = []
        self.output_format = "emacs"
        self.outside_main = True
        self.egyptian = False
        self.notEgyptian = False

    def set_total_errors(self, errors):
        self.total_errors = errors

    def set_filters(self, filters): #TODO: You are going to need to figure out what this will do and how
        self.filters = filters

    def set_output_format(self, format):
        self.output_format = format

    def reset_error_count(self):
        self.total_errors = 0
        self.error_types = {}

    def set_inside_main(self):
        self.outside_main = False

    def check_is_outside_main(self):
        return self.outside_main

    def increment_error_count(self, label, line_num):
        self.total_errors += 1
        if label not in self.error_types:
            self.error_types[label] = 0

        self.error_types[label] += 1
        self.error_tracker.append(StyleError(1, label, line_num))

    def is_egyptian_style(self, egyptian_bool):
        if egyptian_bool:
            self.egyptian = True
        else:
            self.notEgyptian = True
