class StyleError(object):
    """
    Represents a style error in the student's code.
    """

    def __init__(self):
        self.data = dict()
        self.line_num = 0
        self.column_num = 0
        self.points_worth = 0
        self.type = "ERROR"
        self.message = ""

    def __init__(self, points, label, line_num=0, column_num=0, type="ERROR", data={}):
        """
        Log the line number, type and point value of a specific error.
        points (int): Weight of this error.
        label (str): Key for response lookup in list_of_errors.
        line_num (int): Line number of this error.
        column_num (int): Column number of this error.
        data (dictionary): Additional information about the error,
        """

        self.set_data(data)
        self.set_points_worth(points)
        self.set_line_num(line_num)
        self.set_column_num(column_num)
        self.set_message_from_label(label)
        self.set_type(type)

    def __str__(self):
        output_str = ''
        if self.get_line_number():
            output_str += str(self.get_line_number())
            if self.get_column_number():
                output_str += ':' + str(self.get_column_number())
            output_str += '  '
        output_str += str(self.get_message())
        return output_str

    def __gt__(self, other):
        if self.get_line_number() > other.get_line_number():
            return True
        elif self.get_line_number() == other.get_line_number() and self.get_column_number() > other.get_column_number():
            return True
        else:
            return False

    def set_line_num(self, line):
        self.line_num = line
    def set_column_num(self, column):
        self.column_num = column
    def set_message(self, new_message):
        self.message = new_message
    def set_points_worth(self, points):
        self.points_worth = points
    def set_type(self, new_type):
        self.type = new_type
    def set_data(self, new_data):
        self.data = new_data
    def get_points(self):
        return self.points_worth
    def get_message(self):
        return self.message
    def get_line_number(self):
        return self.line_num
    def get_column_number(self):
        return self.column_num
    def get_type(self):
        return self.type
    def get_data(self):
        return self.data

    def set_message_from_label(self, label):
        self.set_message(self.get_error_message(label))

    def get_error_message(self, label):
        return {
            "USING_TABS": "Instead of tabs you must use spaces.  Fix and resubmit your code :).",
            "OPERATOR_SPACING": "Incorrect spacing around {}.".format(self.get_data().get('operator')),
            "BLOCK_INDENTATION": "Incorrect indentation. Expected: {}, found: {}.".format(self.get_data().get('expected'), self.get_data().get('found')),
            "STATEMENTS_PER_LINE": "There should only be one command (statement) on each line.",
            "IF_ELSE_ERROR": "Every If-Else statement should have brackets.",
            "NON_CONST_GLOBAL": "You should never have a non-const global variable.",
            "FUNCTION_LENGTH_ERROR": "Your function is too long. Break it up into separate functions.",
            "LINE_WIDTH": "Line of {} characters exceeded the limit of 90.".format(self.get_data().get('length')),
            "INT_FOR_BOOL": "You need to return true or false, instead of an actual number.",
            "MAGIC_NUMBER": "Store numbers in variables, so that you can give them meaningful names.",
            "BRACE_CONSISTENCY": "Your braces should be either Egyptian or block style, pick one.",
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
            "UNNECESSARY_INCLUDE": "You have included a library we do not allow.",
            "FIRST_CHAR": "First character of a {} name must be capitalized. Expected: {}, found: {}.".format(self.get_data().get("keyword"),
                                                                                                             self.get_data().get("expected"),
                                                                                                             self.get_data().get("found")),
            "OPERATOR_CONSISTENCY": "Your spacing around operators is inconsistent. Pick left, right or both for spacing and stick to it.",
            "POINTER_REFERENCE_CONSISTENCY": "Your use of spacing surrounding '*' and '&' is inconsistent.",
            "MISSING_RME": "{} is missing a complete RME.".format(self.get_data().get("function")),
            "MIN_COMMENTS": "Potentially too few comments. Found {} {} of comments in {} {} of code.".format(self.get_data().get("comments"),
                                                                                                            'line' if self.get_data().get("comments") == 1 else 'lines',
                                                                                                            self.get_data().get("lines"),
                                                                                                            'line' if self.get_data().get("lines") == 1 else 'lines'),
            "DEFINITION_ABOVE_MAIN": "{} is implemented above main. Keep function definitions below main or in a separate .cpp file.".format(self.get_data().get("function")),
            "FOR_LOOP_SEMICOLON_SPACING": "The loop on line {} doesn't have consistent spacing around its semicolons.".format(self.get_data().get("line")),
        }[label]


