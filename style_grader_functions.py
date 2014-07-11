from pyparsing import Literal, Word, Optional, ParseException, alphanums, Keyword
import getopt
import re

def check_if_function(code):
    return_type = Word(alphanums + '_') # Bad style to have "_" but syntactically valid
    function_name = Word(alphanums + '_' + ':')
    args = Word(alphanums + ',' + ' ' + '_')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = return_type + function_name + "(" + Optional(args) + ")"
    grammar = function_declaration + Optional(function_open)
    if len(grammar.searchString(code)):
        return True
    return False

def check_if_switch_statement(code):
    statement = Keyword('switch')
    args = Word(alphanums + '_')
    grammar = statement + Optional(" ") + "(" + args + ")"
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False
def check_if_case_arg(code):
    statement = Keyword('case')
    if len(statement.searchString(code)):
        return True
    else:
        return False

def indent_helper(indentation, tab_size, clean_lines, data_structure_tracker, temp_line_num):
    indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
    results = list()
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.in_block = True
    next_indentation = indentation_size + tab_size

    while data_structure_tracker.in_block:
        temp_line_num += 1
        current_indentation = re.search(r'^( *)\S',
                                        clean_lines.lines[temp_line_num])

        switch_statement = check_if_switch_statement(clean_lines.lines[temp_line_num])

        if switch_statement:
            data_structure_tracker.in_switch = True

        is_break_statement = check_if_break_statement(clean_lines.lines[temp_line_num])

        if is_break_statement and not data_structure_tracker.in_switch:
            results.append({'label': 'UNNECESSARY_BREAK', 'line': temp_line_num + 1})

        if current_indentation:
            line_start = current_indentation.group()
            current_indentation = len(line_start) - len(line_start.strip())

            if current_indentation != next_indentation and line_start.find('}') == -1:
                #check for public: private: and case: exceptions
                if(check_if_public_or_private(clean_lines.lines[temp_line_num]) and \
                        data_structure_tracker.in_class_or_struct) or \
                        (check_if_case_arg(clean_lines.lines[temp_line_num]) and \
                        data_structure_tracker.in_switch):

                    next_indentation -= tab_size
                else:
                    data = {'expected': next_indentation, 'found': current_indentation}
                    results.append({'label': 'BLOCK_INDENTATION', 'line': temp_line_num + 1, 'data': data})


            if clean_lines.lines[temp_line_num].find("{") != -1:
                if data_structure_tracker.in_switch:
                    data_structure_tracker.add_switch_brace("{")
                if data_structure_tracker.in_class_or_struct:
                    data_structure_tracker.add_object_brace("{")
                data_structure_tracker.add_brace("{")
                next_indentation = current_indentation + tab_size

            elif clean_lines.lines[temp_line_num].find("}") != -1:
                end_switch = data_structure_tracker.in_switch
                if data_structure_tracker.in_switch:
                    data_structure_tracker.pop_switch_brace()
                if data_structure_tracker.in_class_or_struct:
                    data_structure_tracker.pop_object_brace()
                data_structure_tracker.pop_brace()
                next_indentation = next_indentation - tab_size

                if end_switch and not data_structure_tracker.in_switch:
                    next_indentation = current_indentation

            if(check_if_public_or_private(clean_lines.lines[temp_line_num]) and
                   data_structure_tracker.in_class_or_struct):
                next_indentation += tab_size

            if check_if_case_arg(clean_lines.lines[temp_line_num]) \
                    and data_structure_tracker.in_switch:
                next_indentation += tab_size


    return results


def check_if_public_or_private(code):

    private = Keyword('private')
    public = Keyword('public')

    grammar = (private | public)

    if len(grammar.searchString(code)) >= 1:
        return True
    else:
        return False


def check_if_break_statement(code):

    statement = Keyword('break')
    grammar = statement + Optional(" ") + ";"
    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

def check_if_struct_or_class(code):
    class_type = Keyword('class')
    struct_type = Keyword('struct')
    name = Word(alphanums + '_')
    statement = (class_type + name | struct_type + name)

    if len(statement.searchString(code)):
        return True
    return False

def check_operator_regex(code, operator):
    """
    If an error has been found, return the column number of the operator, else return 0
    """
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
                    return 0
                if left_symbol == '-' or left_symbol == '=' or left_symbol == '+':
                    return 0
            elif operator == '/':
                if right_symbol == '=':
                    return 0
            elif operator == '=':
                if left_symbol == '+' or left_symbol == '-':
                    return 0
                if right_symbol or left_symbol == '=':
                    return 0
            else:
                # return column number of the error
                return right_not_wspace.regs[0][0] + 1
    else:
        return 0

def print_success():
    print '\033[32mNo errors have been found :)\033[0m'
