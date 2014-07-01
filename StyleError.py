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
            "STRINGSTREAM": "We disallow the use of stringstreams in this course to ensure mastery of other IO methods.",
        }

        self.set_points_worth(points)
        self.set_line_num(line_num)
        self.set_label(list_of_errors[label])

    def __str__(self):
        return '{0}  {1}'.format(self.get_line_number(), self.get_label())

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


