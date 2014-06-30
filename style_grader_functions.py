from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums
import getopt
import re

def check_if_function(code):

    returntype = (Literal("void") | Literal('int') | Literal('string')
                  | Literal('double') | Literal('float') | Literal('char'))
    function_name = Word(alphanums + '_' + ':')
    args = Word(alphanums + ',' + ' ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = returntype + function_name + "(" + Optional(args) + ")"
    grammar = function_declaration + Optional(function_open)

    try:
        grammar.parseString(code)
        return True
    except ParseException:
        return False

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
