class StyleError(object):
    """
    Represents a style error in the student's code.
    """

    def __init__(self):
        self.line_num = 0
        self.column_num = 0
        self.message = ""
        self.points_worth = 0
        self.type = "ERROR"
        self.data = {}

    def __init__(self, points, label, line_num):
        """
        Log the line number, type and point value of a specific error.
        points (int): Weight of this error.
        label (str): Key for response lookup in list_of_errors.
        line_num (int): Line number of this error.
        """

        self.set_points_worth(points)
        self.set_line_num(line_num)
        self.set_column_num(0)
        self.set_message_from_label(label)
        self.type = "ERROR"
        self.data = {}

    def __str__(self):
        output_str = ''
        if self.get_line_number():
            output_str += '{}'.format(self.get_line_number())
            if self.get_column_number():
                output_str += ':{}'.format(self.get_column_number())
            output_str += '  '
        output_str += self.get_message()
        return output_str

    def set_line_num(self, line):
        self.line_num = line
    def set_column_num(self, column):
        self.column_num = column
    def set_message(self, new_message):
        self.message = new_message
    def set_points_worth(self, points):
        self.points_worth = points
    def get_points(self):
        return self.points_worth
    def get_message(self):
        return self.message
    def get_line_number(self):
        return self.line_num
    def get_column_number(self):
        return self.column_num

    def set_message_from_label(self, label):
        self.set_message(self.get_error_message(label))

    def get_error_message(self, label):
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

        return list_of_errors[label]

