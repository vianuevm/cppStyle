from collections import Counter
import getopt
import re

from pyparsing import Literal, Word, Optional, ParseException, alphanums, Keyword, srange

class EmptyFileException(object):
    pass

def get_indent_level(filename):
    data = filename.readlines()
    indent_re = re.compile('^\s+\w')
    results = []
    for line in data:
        match = indent_re.search(line)
        if match:
            results.append(len(match.group(0))-1)
    return Counter(results).most_common(1)[0] if results else 4

def check_if_function(code):
    return_type = Word(alphanums + '_[]') # Bad style to have "_" but syntactically valid
    function_name = Word(alphanums + '_:')
    args = Word(alphanums + ',_[]&* ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = Optional(srange("[a-z]")) + return_type + function_name + "(" + Optional(args) + ")"
    grammar = function_declaration + Optional(function_open)
    if len(grammar.searchString(code)):
        return True
    return False

def check_if_function_prototype(code):
    return_type = Word(alphanums + '_[]') # Bad style to have "_" but syntactically valid
    function_name = Word(alphanums + '_:')
    args = Word(alphanums + ',_[]&* ')
    function_open = Literal("{")
    function_close = Literal("}")
    function_declaration = return_type + function_name + "(" + Optional(args) + ")" + Optional(" ") + ";"
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
    if not indentation:
        return results
    indentation = indentation.group()
    indentation_size = len(indentation) - len(indentation.strip())
    data_structure_tracker.in_block = True
    next_indentation = indentation_size + tab_size

    while data_structure_tracker.in_block:
        temp_line_num += 1
        try:
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


                if clean_lines.lines[temp_line_num].find("{") != -1 and clean_lines.lines[temp_line_num].find("}") != -1:
                    # nothing to adjust
                    continue

                elif clean_lines.lines[temp_line_num].find("{") != -1:
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

        except IndexError:
            data_structure_tracker.in_block = False


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


def check_operator_spacing_around(code, operator):
    """Check for correct spacing around the given operator in the line.

    There should be exactly one space on either side of the given operator.
    Notice that operators `*` and `&` don't quite follow this rule, since we're
    okay with `Foo* foo` or `Foo *foo` for pointers, as long as they're
    consistent about it.

    :param str code: The line of code to check.
    :param str operator: The operator to check, such as "+"
    :returns: The column number of the inconsistent operator, or `None`
              otherwise. Notice that the column number may be `0`, so you must
              not check for falsiness, but rather check that
              `result is not None`.
    :rtype: int or None

    """
    operator_regex = re.compile(r"""
        (?P<code_left>\S+)
        (?P<whitespace_left>\s*)
        (?P<operator>{operator})
        (?P<whitespace_right>\s*)
        (?P<code_right>\S+)
    """.format(
        operator=re.escape(operator)
    ), re.VERBOSE)

    whitespace_groups = ["whitespace_left", "whitespace_right"]
    for match in operator_regex.finditer(code):
        for group in whitespace_groups:
            if match.group(group) != " ":
                return match.start("operator")
    return None


def print_success():
    print 'No errors found'
