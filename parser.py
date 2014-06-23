from cpplint import RemoveMultiLineComments
from cpplint import CleansedLines
from cpplint import GetPreviousNonBlankLine
import codecs
import copy
import getopt
import math  # for log
import os
import re
import sre_compile
import string
import sys
import unicodedata

#TODO FIRST THING ON THE LIST IS INDENTATION FUNCTIONS


 #TODO This is on line 1695 cpplint
 ## Remember initial indentation level for this class.  Using raw_lines here
 #   # instead of elided to account for leading comments.
 #   initial_indent = Match(r'^( *)\S', clean_lines.raw_lines[linenum])
 #   if initial_indent:
 #     self.class_indent = len(initial_indent.group(1))
 #   else:
 #     self.class_indent = 0


OPERATOR_SPACE_ERROR = "Incorrect spacing around operators"
INDENTATION_ERROR = "Incorrect indentation.  Check to make sure you are four spaces in from previous code block."
COMMAND_ERROR = "There should only be one command (statement) on each line.  Ever."
IF_ELSE_ERROR = "Every If-Else statement should have brackets, regardless."
GLOBAL_VARIABLE = "You should never, ever, ever... wait for it... ever have a non-const global variable."
FUNCTION_LENGTH_ERROR = "Your function should not be this long.  Break it up into separate functions."
LINE_WIDTH = "You exceeded 80 chars on a line.  This needs to be reformatted."
BOOL_VALUE = "You need to return true or false.  Not 1 or 0."
MAGIC_NUMBER = "Every number should be stored in a variable, not used as a literal."
BRACES_ERROR = "Your braces should be egyption style or block style.  You have some kind of formatting error."
SPACING_ERROR = "Use tabs or spaces, not both."
UNNECESSARY_BREAK = "Breaks should ONLY be used in switch statements.  Fix your logic."
GOTO = "Never use the goto function."

class Default_Filters():

    def __init__(self):
        self.goto = True
        self.globals = True
        self.breaks = True

DEFAULT_FILTERS = Default_Filters()
OUTSIDE_MAIN = True


class StyleError():
    def __init__(self):
        self.line_num = 0
        self.label = ""
        self.points_worth = 0

    def __init__(self, points, label, line_num):
        if label == OPERATOR_SPACE_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(OPERATOR_SPACE_ERROR)
        elif label == INDENTATION_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(INDENTATION_ERROR)
        elif label == COMMAND_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(COMMAND_ERROR)
        elif label == IF_ELSE_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(IF_ELSE_ERROR)
        elif label == GLOBAL_VARIABLE:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(GLOBAL_VARIABLE)
        elif label == FUNCTION_LENGTH_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(FUNCTION_LENGTH_ERROR)
        elif label == LINE_WIDTH:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(LINE_WIDTH)
        elif label == BOOL_VALUE:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(BOOL_VALUE)
        elif label == MAGIC_NUMBER:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(MAGIC_NUMBER)
        elif label == BRACES_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(BRACES_ERROR)
        elif label == SPACING_ERROR:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(SPACING_ERROR)
        elif label == UNNECESSARY_BREAK:
            self.setPointsWorth(1)
            self.setLineNum(line_num)
            self.setLabel(UNNECESSARY_BREAK)
        else:
            assert "UNRECOGNIZED ERROR LABEL"

    def setLineNum(self, line):
        self.line_num = line
    def setLabel(self, label_name):
        self.label = label_name
    def setPointsWorth(self, points):
        self.points_worth = points
    def getPoints(self):
        return self.points_worth
    def getLabel(self):
        return self.label
    def getLineNum(self):
        return self.line_num


class DataStructureTracker():
    def __init__(self):
        self.in_block = False
        self.brace_stack = []
        self.brace_index = 1
        self.length_so_far = 0

    def getLength(self):
        return self.length_so_far

    def setInBlock(self, boolVar):
        self.in_block = boolVar

    def isInBlock(self):
        return self.in_block

    def addBrace(self, brace):
        self.brace_stack.append(brace)
        self.brace_index += 1

    def popBrace(self):
        self.brace_stack.pop()
        self.brace_index -= 1
        if self.brace_index == 0:
            self.isInFunction(False)

    def getBraceIndex(self):
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

    def addEvent(self, amount):
        self.add += amount
        self.total += amount

    def subEvent(self, amount):
        self.sub += amount
        self.total += amount

    def greaterEvent(self, amount):
        self.greater += amount
        self.total += amount

    def lessEvent(self, amount):
        self.less += amount
        self.total += amount

    def divideEvent(self, amount):
        self.divide += amount
        self.total += amount

    def modEvent(self, amount):
        self.mod += amount
        self.total += amount



class StyleRubric(object):
    """ This class sets all variable aspects of grading (whitespace, gotos etc)
    """
    def __init__(self):
        self.total_errors = 0
        self.filters = DEFAULT_FILTERS
        self.error_types = {}
        self.error_tracker = []
        self.output_format = "emacs"
        self.outside_main = True

    def setTotalErrors(self, errors):
        self.total_errors = errors

    def setFilters(self, filters): #TODO: You are going to need to figure out what this will do and how
        self.filters = filters

    def setOutPutFormat(self, format):
        self.output_format = format

    def resetErrorCount(self):
        self.total_errors = 0
        self.error_types = {}

    def setInsideMain(self):
        self.outside_main = False

    def isOutsideMain(self):
        return self.outside_main

    def incrementErrorCount(self, label, line_num):
        self.total_errors += 1

        if label not in self.error_types:
            self.error_types[label] = 0

        self.error_types[label] += 1
        self.error_tracker.append(StyleError(1, label, line_num))



def validReturn(filename, clean_lines, line, line_num, rubric):
    code = clean_lines.lines
    current_line = code[line_num]
    returnVal = re.search(r'\s+return\s+', current_line)

    if(returnVal): #make sure it's not the end of a word
        list_of_line = current_line.split(' ')
        if len(list_of_line) > 2:
            #TODO Figure out what you want to take off with a more than one statement on return line
            print "do the to do"
        else:
            current_line = current_line[6:].strip()
            if(current_line.isdigit()):
                rubric.incrementErrorCount(MAGIC_NUMBER, line_num)

def numOfCommands(filename, clean_lines, line, line_num, rubric):
    cleansed_line = clean_lines.lines[line_num]
    #This code is taken directly from cpplint lines 3430-3440
    if (cleansed_line.count(';') > 1 and
      # for loops are allowed two ;'s (and may run over two lines).
        cleansed_line.find('for') == -1 and
        (GetPreviousNonBlankLine(clean_lines, line_num)[0].find('for') == -1 or
        GetPreviousNonBlankLine(clean_lines, line_num)[0].find(';') != -1) and
        # It's ok to have many commands in a switch case that fits in 1 line
        not ((cleansed_line.find('case ') != -1 or
        cleansed_line.find('default:') != -1) and
        cleansed_line.find('break;') != -1)):
        rubric.incrementErrorCount(COMMAND_ERROR, line_num)

def lineWidthCheck(filename, clean_lines, line, line_num, rubric):
    max_length = 80
    current_length = len(line)
    if current_length > max_length:
        rubric.incrementErrorCount(LINE_WIDTH, line_num)

def operatorSpacing(filename, clean_lines, line, line_num, operator_space_tracker, rubric):
    code = clean_lines.lines[line_num]
    matches = []
    if not checkOperatorRegEx(code, '\+')  or \
        not checkOperatorRegEx(code, '\-') or \
        not checkOperatorRegEx(code, '\/') or \
        not checkOperatorRegEx(code, '\%') or \
        not checkOperatorRegEx(code, '\*'):
        rubric.incrementErrorCount(OPERATOR_SPACE_ERROR, line_num)
    else:
        return True

def checkOperatorRegEx(code, operator):

    regexOne = r'' + '\S+' + operator
    regexTwo =  r'' + operator + '\S+'
    #check to see if there is a non-whitespace character on either side of the operator
    if re.search(regexOne, code) or re.search(regexTwo, code):
        return False
    else:
        return True

def checkGoTo(clean_lines, line, line_num, rubric):
    code = clean_lines.lines[line_num]

    match = re.search(r'\s+gotos\+', code)
    if(match):
        rubric.incrementErrorCount(GOTO, line_num)

def nonConstGlobal(filename, clean_lines, line_num, rubric):
    code = clean_lines.lines[line_num]

    if re.search(r'int main', code):
        rubric.setInsideMain()

    if(rubric.isOutsideMain()):
        function = re.search(r'(\w(\w|::|\*|\&|\s)*)\(', code)
        variable = re.search(r'^\s*(int|string|char|bool)\s+', code)
        if not function and variable:
            rubric.incrementErrorCount(GLOBAL_VARIABLE, line_num)


def indentationStation(filename, clean_lines, line, line_num, operator_space_tracker, rubric):

    tab_size = 4
    code = clean_lines.lines[line_num]
    stripped_code = code.strip()
    function = re.search(r'(\w(\w|::|\*|\&|\s)*)\(', code)
    if_statement = re.search(r'^if\s*\(\s*', stripped_code)
    else_if_statement = re.search(r'^else\s*\(', code)
    else_statement = re.search(r'^else\s+', code)
    switch_statement = re.search(r'^switch\s*\(', stripped_code)

    indentation = re.search(r'^( *)\S', code)
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())

    if function or rubric.isOutsideMain():
        if indentation_size != 0:
            rubric.incrementErrorCount(INDENTATION_ERROR, line_num)
        if rubric.isOutsideMain():
            return

    #TODO: Need to check indentation ON the same line as the function still
    if function:
        if not code.find('{'):
            second_line = clean_lines.lines[line_num + 1]

            if code.find('{'):
                temp_line_num = line_num
                data_structure_tracker = DataStructureTracker()
                checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
            else:
                #TODO Figure out what it means to not have braces in the right place
                pass
        else:
            temp_line_num = line_num
            data_structure_tracker = DataStructureTracker()
            checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
    elif if_statement:
        temp_line_num = line_num
        data_structure_tracker = DataStructureTracker()
        checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
    elif switch_statement:
        temp_line_num = line_num
        data_structure_tracker = DataStructureTracker()
        checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
    elif else_if_statement:
        temp_line_num = line_num
        data_structure_tracker = DataStructureTracker()
        checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
    elif else_statement:
        temp_line_num = line_num
        data_structure_tracker = DataStructureTracker()
        checkCurrentBlockIndentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker, temp_line_num)
    else:
        return


def checkCurrentBlockIndentation(indentation, tab_size, code, rubric, clean_lines,
                                 data_structure_tracker, temp_line_num):


    indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.setInBlock(True)
    next_indentation = indentation_size + tab_size

    while data_structure_tracker.isInBlock():
        temp_line_num += 1
        current_indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
        line_start = current_indentation.group()
        current_indentation = len(line_start) - len(line_start.strip())
        if current_indentation != next_indentation and line_start.find('}') == -1:
            rubric.incrementErrorCount(INDENTATION_ERROR, temp_line_num)
        if clean_lines.lines[temp_line_num].find("{") != -1:
            data_structure_tracker.addBrace("{")
            next_indentation = current_indentation + tab_size
        elif clean_lines.lines[temp_line_num].find("}") != -1:
            data_structure_tracker.popBrace()
            next_indentation = current_indentation - tab_size




def parseCurrentLine(filename, clean_lines, line, line_num, operator_space_tracker, rubric):

    #TODO
    nonConstGlobal(filename, clean_lines, line_num, rubric)
    validReturn(filename, clean_lines, line, line_num, rubric)
    numOfCommands(filename, clean_lines, line, line_num, rubric)
    checkGoTo(clean_lines, line, line_num, rubric)

    #Check for mixed tabs/spaces and log error #TODO: This can wait
    lineWidthCheck(filename, clean_lines, line, line_num, rubric)
    #Check for unnecessary includes
    operatorSpacing(filename, clean_lines, line, line_num, operator_space_tracker, rubric)
    #Call BRACES function to check for correct bracing
    #Call function or checking INDENTATION!!
    indentationStation(filename, clean_lines, line, line_num, operator_space_tracker, rubric) #TODO THIS IS UNDER CONSTRUCTION


def processStudentFile(student_code, rubric, filename, operator_space_tracker):
    error = ""
    RemoveMultiLineComments(filename, student_code, error)
    clean_lines = CleansedLines(student_code)
    code = clean_lines.lines
    line_num = 0
    for line in code:
        parseCurrentLine(filename, clean_lines, line, line_num, operator_space_tracker, rubric)
        line_num += 1


def gradeStudentFile(filename, rubric, operator_space_tracker):

    try:
        student_code = codecs.open(filename, 'r', 'utf8', 'replace').read().split('\n')
        line = 0
        newline = False
        x = 0
        for x in range(x, len(student_code)):
            ending = student_code[x][-1]
            if ending == '\r':
                student_code[x] = student_code[x].rstrip('\r')
                newline = True
            else:
                newline = False

        location = filename.find('.') + 1 #This avoids getting the period character
        extension = filename[location:]

        if extension != 'cpp':
            sys.stderr.write("Incorrect file type")
            return

    except IOError:
        sys.stderr.write(
            "This file could not be read: '%s.'  Please check filename and resubmit \n" % filename)
        return

    processStudentFile(student_code, rubric, filename, operator_space_tracker)
    return

def getArguments(argv):
    try:
        (opts, filenames) = getopt.getopt(argv, '', ['whitespace=', 'globalconst=', 'verbose=',
                                                     'counting=',
                                                     'filter=',
                                                     'root=',
                                                     'linelength=',
                                                     'extensions='])

    except getopt.GetoptError:
        print('Invalid arguments.')

    return argv


def main():
    print "Hello World"
    operator_space_tracker = OperatorSpace()
    rubric = StyleRubric()
    student_file_names = getArguments(sys.argv[1:])
    sys.stderr = codecs.StreamReaderWriter(sys.stderr, #TODO: Set up standard error to print properly
                                         codecs.getreader('utf8'),
                                         codecs.getwriter('utf8'),
                                         'replace')
    rubric.resetErrorCount()



    for filename in student_file_names:
        gradeStudentFile(filename, rubric, operator_space_tracker)
    #function called on each filename function(fileName, rubric)

#print / send results
if __name__ == '__main__':
    main()
