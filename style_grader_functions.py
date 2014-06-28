from cpplint import RemoveMultiLineComments, CleansedLines, GetPreviousNonBlankLine
from style_grader_classes import DefaultFilters, StyleError, DataStructureTracker, OperatorSpace, StyleRubric
from pyparsing import Literal, Word, Optional, ParseBaseException, alphanums
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


def valid_return(filename, clean_lines, line, line_num, rubric):
    code = clean_lines.lines
    current_line = code[line_num]
    returnVal = re.search(r'\s+return\s+', current_line)

    if returnVal: 
        # make sure it's not the end of a word
        list_of_line = current_line.split(' ')
        if len(list_of_line) > 2:
            #TODO Figure out what you want to take off with a more than one statement on return line
            pass
        else:
            current_line = current_line[6:].strip()
            if current_line.isdigit():
                rubric.add_error("BOOL_VALUE", line_num)


def num_of_commands(filename, clean_lines, line, line_num, rubric):
    cleansed_line = clean_lines.lines[line_num]
    # This code is taken directly from cpplint lines 3430-3440
    if (cleansed_line.count(';') > 1 and
        # for loops are allowed two ;'s (and may run over two lines).
        cleansed_line.find('for') == -1 and
        (GetPreviousNonBlankLine(clean_lines, line_num)[0].find('for') == -1 or
        GetPreviousNonBlankLine(clean_lines, line_num)[0].find(';') != -1) and
        # It's ok to have many commands in a switch case that fits in 1 line
        not ((cleansed_line.find('case ') != -1 or
        cleansed_line.find('default:') != -1) and
        cleansed_line.find('break;') != -1)):
        
        rubric.add_error("COMMAND_ERROR", line_num)


def line_width_check(filename, clean_lines, line, line_num, rubric):
    max_length = 80
    current_length = len(line)
    if current_length > max_length:
        rubric.add_error("LINE_WIDTH", line_num)


def operator_spacing(filename, clean_lines, line, line_num, operator_space_tracker, rubric):
    code = clean_lines.lines[line_num]
    matches = []
    if not check_operator_regex(code, '\+')  or \
        not check_operator_regex(code, '\-') or \
        not check_operator_regex(code, '\/') or \
        not check_operator_regex(code, '\%') or \
        not check_operator_regex(code, '\*'):
        rubric.add_error("OPERATOR_SPACE_ERROR", line_num)

    else:
        return True


def check_operator_regex(code, operator):
    regex_one = r'' + '\S+' + operator
    regex_two =  r'' + operator + '\S+'



    #check to see if there is a non-whitespace character on either side of the operator
    if re.search(regex_one, code) or re.search(regex_two, code):

        left_not_wspace = re.search(regex_one, code)
        right_not_wspace = re.search(regex_two, code)

        if right_not_wspace and left_not_wspace:
            left_code = left_not_wspace.group()
            right_code = right_not_wspace.group()
            left_symbol = left_code[-2]
            right_symbol = right_code[1]
            operator = right_symbol[0]

            if operator == '+' or operator == '-':
                if right_symbol == '-' or right_symbol == '=' or right_symbol == '+':
                    return  True
                if left_symbol == '-' or left_symbol == '=' or left_symbol == '+':
                    return True
            elif operator == '/':
                if right_symbol == '=':
                    return True
            elif operator == '=':
                if left_symbol == '+' or left_symbol == '-':
                    return True
                if right_symbol or left_symbol == '=':
                    return True

            else:
                return False
    else:
        return True


def check_go_to(clean_lines, line, line_num, rubric):
    code = clean_lines.lines[line_num]

    match = re.search(r'\s+gotos\+', code)
    if match :
        rubric.add_error("GOTO", line_num)


def check_non_const_global(filename, clean_lines, line_num, rubric):
    code = clean_lines.lines[line_num]

    if re.search(r'int main', code):
        rubric.set_inside_main()

    if rubric.is_outside_main():
        function = check_if_function(code)
        variable = re.search(r'^\s*(int|string|char|bool)\s+', code)
        if not function and variable:
            rubric.add_error("GLOBAL_VARIABLE", line_num)


def check_brace_consistency(clean_lines, line, line_num, rubric):
    code = clean_lines.lines[line_num]
    stripped_code = code.strip()
    function = check_if_function(code)
    if_statement = re.search(r'^if\s*\(\s*', stripped_code)
    else_if_statement = re.search(r'^else\s*\(', code)
    else_statement = re.search(r'^else\s+', code)
    switch_statement = re.search(r'^switch\s*\(', stripped_code)

    if function or if_statement or else_statement or switch_statement:

        if function and clean_lines.lines[line_num + 1].find('{') != -1 or\
            else_if_statement and clean_lines.lines[line_num + 1].find('{') != -1 or\
            else_statement and clean_lines.lines[line_num + 1].find('{') != -1 or\
            switch_statement and clean_lines.lines[line_num + 1].find('{') != -1 or\
                if_statement and clean_lines.lines[line_num + 1].find('{') != -1:

            rubric.set_egyptian_style(False)
        elif function and code.find('{') != -1 or \
                else_if_statement and code.find('{') != -1 or\
                else_statement and code.find('{') != -1 or\
                switch_statement and code.find('{') != -1 or\
                if_statement and code.find('{') != -1:

            rubric.set_egyptian_style(True)
        elif not rubric.is_outside_main():
            rubric.add_error("BRACES_ERROR", line_num)

        #if both of these are true, they are not consistent, therefore error.
        if rubric.notEgyptian:
            if rubric.egyptian:
                rubric.add_error("BRACES_ERROR", line_num)


def check_function_block_indentation(filename, clean_lines, line, line_num,
                                     operator_space_tracker, rubric):

    tab_size = 4
    code = clean_lines.lines[line_num]
    stripped_code = code.strip()
    function = check_if_function(code)
    if_statement = re.search(r'^if\s*\(\s*', stripped_code)
    else_if_statement = re.search(r'^else\s*\(', code)
    else_statement = re.search(r'^else\s+', code)
    switch_statement = re.search(r'^switch\s*\(', stripped_code)

    indentation = re.search(r'^( *)\S', code)
    if indentation:
        indentation = indentation.group()
        indentation_size = len(indentation) - len(indentation.strip())
    else:
        return

    if function or rubric.is_outside_main():
        if indentation_size != 0:
            rubric.add_error("INDENTATION_ERROR", line_num)
        if rubric.is_outside_main():
            return

    #TODO: Need to check indentation ON the same line as the function still
    if function:
        #if not egyptian style
        if code.find('{') == -1:
            second_line = clean_lines.lines[line_num + 1]

            if code.find('{'):
                temp_line_num = line_num + 1
                data_structure_tracker = DataStructureTracker()
                data_structure_tracker.brace_stack.append('{')
                process_current_blocks_indentation(indentation, tab_size, code, rubric,
                                         clean_lines, data_structure_tracker,
                                         temp_line_num)
            else:
                #TODO Figure out what it means to not have braces in the right place
                pass
        else:
            temp_line_num = line_num
            data_structure_tracker = DataStructureTracker()
            data_structure_tracker.brace_stack.append('{')
            process_current_blocks_indentation(indentation, tab_size, code, rubric,
                                               clean_lines, data_structure_tracker,
                                               temp_line_num)
    else:
        return


def process_current_blocks_indentation(indentation, tab_size, code, rubric, clean_lines,
                                       data_structure_tracker, temp_line_num):

    indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.set_is_in_block(True)
    next_indentation = indentation_size + tab_size

    while data_structure_tracker.check_is_in_block():
        temp_line_num += 1
        current_indentation = re.search(r'^( *)\S',
                                        clean_lines.lines[temp_line_num])
        if current_indentation:
            line_start = current_indentation.group()
            current_indentation = len(line_start) - len(line_start.strip())
            if current_indentation != next_indentation and line_start.find('}') == -1:
                rubric.add_error("INDENTATION_ERROR", temp_line_num)
            if clean_lines.lines[temp_line_num].find("{") != -1:
                data_structure_tracker.add_brace("{")
                next_indentation = current_indentation + tab_size
            elif clean_lines.lines[temp_line_num].find("}") != -1:
                data_structure_tracker.pop_brace()
                next_indentation = next_indentation - tab_size


def parse_current_line_of_code(filename, clean_lines, line, line_num,
                               operator_space_tracker, rubric):

    #Clear
    check_non_const_global(filename, clean_lines, line_num, rubric)
     #Only one statement on the return line?
    valid_return(filename, clean_lines, line, line_num, rubric)
    #One statement per line
    num_of_commands(filename, clean_lines, line, line_num, rubric)
    #check to see if the line contains a goto function
    check_go_to(clean_lines, line, line_num, rubric)
    #Check for mixed tabs/spaces and log error #TODO: This can wait
    line_width_check(filename, clean_lines, line, line_num, rubric)
    #Check for unnecessary includes
    #TODO: Above duh.

    #Check for operator Spacing
    operator_spacing(filename, clean_lines, line, line_num, operator_space_tracker, rubric)

    #Call function or checking INDENTATION!!
    check_function_block_indentation(filename, clean_lines, line, line_num, operator_space_tracker,
                       rubric)
                       #TODO THIS IS UNDER CONSTRUCTION
    #Check for braces being consistent (egyptian or non-egyptian)
    check_brace_consistency(clean_lines, line, line_num, rubric)


def process_current_student_file(student_code, rubric, filename, operator_space_tracker):
    error = ""
    RemoveMultiLineComments(filename, student_code, error)
    clean_lines = CleansedLines(student_code)
    code = clean_lines.lines
    line_num = 0
    for line in code:
        parse_current_line_of_code(filename, clean_lines, line, line_num, operator_space_tracker, rubric)
        line_num += 1


def grade_student_file(filename, rubric, operator_space_tracker):
    try:
        student_code = codecs.open(filename, 'r', 'utf8', 'replace').read().split('\n')
        newline = False
        x = 0
        ending = ''
        for x in range(x, len(student_code)):
            if len(student_code[x]) > 0:
                ending = student_code[x][-1]
            if ending == '\r':
                student_code[x] = student_code[x].rstrip('\r')
                newline = True
            else:
                newline = False

        # This avoids getting the period character

        location = filename.find('.') + 1
        extension = filename[location:]

        if extension not in ['h', 'cpp']:
            sys.stderr.write("Incorrect file type")
            return

    except IOError:
        sys.stderr.write(
            "This file could not be read: '%s.'  "
            "Please check filename and resubmit \n" % filename)
        return

    process_current_student_file(student_code, rubric, filename, operator_space_tracker)
    return


def get_arguments(argv):
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


def check_if_function(code):

    returntype = (Literal("void") | Literal('int') | Literal('string')
                  | Literal('double') | Literal('float') | Literal('char'))
    function_name = Word(alphanums + '_')
    args = Word(alphanums + ',' + ' ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = returntype + function_name + "(" + Optional(args) + ")"
    grammar = function_declaration + Optional(function_open)

    try:
        grammar.parseString(code)
        return True
    except ParseBaseException:
        return False
