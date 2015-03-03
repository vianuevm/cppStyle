from style_grader_functions import check_if_function, check_if_function_prototype
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, srange
import re


def check_function_def_above_main(self, code):
    prototype = check_if_function_prototype(code)
    function = check_if_function(code)
    inside = Literal("int main")
    if len(inside.searchString(code)):
        return
    elif function and not prototype and self.outside_main:
        function_regex = re.compile("^\s*(\w+)\s+(\w+)")
        match = function_regex.search(code)
        function_name = match.group(2) if match else "NOT_FOUND"
        self.add_error(label="DEFINITION_ABOVE_MAIN", data={'function': function_name})


def check_int_for_bool(self, code):
    if check_if_function(code):
        function_regex = re.compile("^\s*(\w+)\s+(\w+)")
        match = function_regex.search(code)
        if match:
            self.current_function = (match.group(1), match.group(2))
    current_function = getattr(self, "current_function", ("", ""))

    return_regex = re.compile("\s*return\s+(\w+)")
    match = return_regex.search(code)
    if match and match.group(1).isdigit() and current_function[0] == "bool":
        self.add_error(label="INT_FOR_BOOL")

# New operator spacing function
def check_operator_spacing(self, code):
    # Check normal operators
    # account for *=, %=, /=, +=, -=
    indexes = []
    indexes = findOccurences(code, '+') + \
              findOccurences(code, '-') + \
              findOccurences(code, '%') + \
              findOccurences(code, '*') + \
              findOccurences(code, '/') + \
              findOccurences(code, '!') + \
              findOccurences(code, '>') + \
              findOccurences(code, '<') + \
              findOccurences(code, '=') + \
              findOccurences(code, '&') + \
              findOccurences(code, '|')
    indexes.sort()  # Force compound operator indexes to be correctly ordered

    skip_next = False
    for operator_index in indexes:
        if skip_next:
            # skip second operator in compound/increment/decrement operator
            skip_next = False
            continue
        
        if is_increment_decrement(code, operator_index):
            # Don't worry about increment/decrement operators
            skip_next = True
        elif is_compound_operator(code, operator_index):
            skip_next = True
            if not operator_helper(True, code, operator_index):
                self.add_error(label='OPERATOR_SPACING', column=operator_index,
                                data={'operator': code[operator_index:operator_index + 2]})
        else:
            # Add code checking for unary + and - operators
            if code[operator_index] == '!':
                index = operator_index - 1
                if code[index]:
                    if code[index] != ' ' and code[index] != '\r' and \
                        code[index] != '\n' and code[index] != '(':
                            self.add_error(label='OPERATOR_SPACING', column=operator_index, data={'operator': code[operator_index]})
            elif not operator_helper(False, code, operator_index):
                self.add_error(label='OPERATOR_SPACING', column=operator_index, data={'operator': code[operator_index]})

def is_increment_decrement(code, index):
    if code[index + 1]:
        if code[index] in ['+', '-'] and code[index + 1] == code[index]:
            return True
    return False

def is_compound_operator(code, index):
    if code[index + 1]:
        # Check for +=, -=, *=, /=, %=, >=, <=, ==, !=
        if code[index] in ['>', '<', '*', '/', '+', '-', '!', '=', '%']:
            if code[index + 1] == '=':
                return True
        # Check &&, ||
        elif code[index] in ['&', '|']:
            if code[index + 1] == code[index]:
                return True
    return False

def operator_helper(compound, code, index):
    correct_spacing = True
    if compound:
        if code[index + 2] and code[index + 2] != '\r' and code[index + 2] != '\n' and code[index + 2] != ' ':
            correct_spacing = False
        if code[index - 1] and code[index - 1] != ' ':
            correct_spacing = False
    else:
        if code[index + 1] and code[index + 1] != '\r' and code[index + 1] != '\n' and code[index + 1] != ' ':
            correct_spacing = False
        if code[index - 1] and code[index - 1] != ' ':
            correct_spacing = False
    return correct_spacing

def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]
def findMultiOccurences(s, sub):
    occurences = []
    loc = 0
    while s.find(sub, loc) != -1:
        occurences.append(s.find(sub, loc))
        loc = occurences[-1] + 1 # find is inclusive of start, must move forward 1
    return occurences

def check_equals_true(self, code):
    keyword = Literal("true") | Literal("false")
    statement_parser = Group("==" + keyword) | Group(keyword + "==")
    if len(statement_parser.searchString(code)):
        self.add_error(label="EQUALS_TRUE")


def check_goto(self, code):
    # Hacky but gets the job done for now - has holes though
    q_goto = re.compile('\".*goto.*\"')
    r_goto = re.compile('(?:\s+|^|\{)goto\s+')
    if r_goto.search(code) and not q_goto.search(code):
        self.add_error(label="GOTO")


def erase_string(code):
    # remove contents of literal strings
    code = code.replace("\\\"", "") # remove escaped quotes
    results = re.findall(r'"(.*?)"', code)
    for string in results:
        quote_mark = "\""
        code = code.replace(quote_mark + string + quote_mark, "\"\"")

    # remove contents of literal chars
    code = code.replace('\\\\', '') # replace escaped backslash
    code = code.replace("\\'", "") # remove escaped single quote
    results = re.findall(r"'(.*?)'", code)
    for string in results:
        single_quote_mark = "'"
        code = code.replace(single_quote_mark + string + single_quote_mark, "''")
    return code


def check_define_statement(self, code):
    q_define = re.compile('\".*(?:\s+|^)#\s*define\s+.*\"')
    r_define = re.compile('(?:\s+|^)#\s*define\s+')
    if r_define.search(code) and not q_define.search(code):
        words = code.split()
        # They shouldn't be using __MY_HEADER_H__ because __-names are
        # reserved, but we'll allow it anyways.
        legal_endings = ["_H", "_H__"]
        if not any(words[-1].endswith(i) for i in legal_endings):
            self.add_error(label="DEFINE_STATEMENT")


def check_continue(self, code):
    # Hacky but gets the job done for now - has holes though
    q_continue = re.compile('\".*continue.*\"')
    r_continue = re.compile('(?:\s+|^|\{)continue\s*;')
    if r_continue.search(code) and not q_continue.search(code):
        self.add_error(label="CONTINUE_STATEMENT")


def check_ternary_operator(self, code):
    q_ternary = re.compile('\".*\?.*\"')
    r_ternary = re.compile('\?')
    if r_ternary.search(code) and not q_ternary.search(code):
        self.add_error(label="TERNARY_OPERATOR")


def check_while_true(self, code):
    statement_parser = Literal("while") + Literal("(") + Literal("true") + Literal(")")
    if len(statement_parser.searchString(code)):
        self.add_error(label="WHILE_TRUE")


def check_non_const_global(self, code):
    inside = Literal("int main")
    if len(inside.searchString(code)):
        self.outside_main = False

    if self.outside_main:
        function = check_if_function(code)
        variables = variables = re.compile("^(?:\w|_)+\s+(?:\w|_|\[|\])+\s*=\s*.+;")
        keywords = re.compile("^\s*(?:using|class|struct)")
        constants = re.compile("^\s*(?:static\s+)?const")
        if not function and variables.search(code) and \
                not keywords.search(code) and \
                not constants.search(code):
            self.add_error(label="NON_CONST_GLOBAL")


def check_main_syntax(self, code):
    # Return value for main is optional in C++11
    parser = Literal("int") + Literal("main") + Literal("(") + SkipTo(Literal(")")) + Literal(")")
    if len(parser.searchString(code)):
        main_prefix = Literal("int") + Literal("main") + Literal("(")
        full_use = Literal("int") + "argc" + "," + Optional("const") + "char" + "*" + "argv" + "[" + "]" + ")"
        # 3 options for main() syntax
        if not len((main_prefix + Literal(")")).searchString(code)) and \
                not len((main_prefix + Literal("void") + Literal(")")).searchString(code)) and \
                not len((main_prefix + full_use).searchString(code)):
            self.add_error(label="MAIN_SYNTAX")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def check_first_char(self, code):
    # check if the first char is lower-case alpha or '_'
    lowercase = re.compile("(?:^|\s+)(?:class|struct)\s+(?:[a-z]|_)\w+")
    bad_naming = lowercase.search(code)
    if bad_naming:
        result = bad_naming.group(0).split()
        self.add_error(label="FIRST_CHAR",
                       data={"keyword": result[0],
                             "expected": str(result[1]).capitalize(),
                             "found": str(result[1])})


def check_unnecessary_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('<') + Word(alphanums)
    try:
        grammar.parseString(code)
        begin = code.find("<")
        end = code.find(">")
        included_library = code[begin + 1:end]
        if included_library not in self.includes:
            self.add_error(label="UNNECESSARY_INCLUDE")
    except ParseException:
        return


def check_local_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('"') + Word(alphanums)
    try:
        grammar.parseString(code)
        begin = code.find('"')
        included_file = code[begin + 1:]
        end = included_file.find('"')
        included_file = included_file[:end]
        if included_file not in self.includes:
            self.local_includes[self.current_file].append(included_file)
    except ParseException:
        return


def check_for_loop_semicolon_spacing(self, code):
    # Match the semicolons and any whitespace around them.
    for_loop_regex = re.compile(
        r"""
        \s*for\s*\(
            (?P<code1>[^;]*?)

            (?P<semicolon1>\s*;\s*)

            (?P<code2>[^;]*?)

            (?P<semicolon2>\s*;\s*)

            (?P<code3>[^;]*?)
        \)
        """,
        re.VERBOSE
    )
    match = for_loop_regex.search(code)
    if not match:
        return

    self.for_loop_spacing_before = getattr(self, "for_loop_spacing_before", None)
    self.for_loop_spacing_after = getattr(self, "for_loop_spacing_after", None)

    semicolon1 = match.group("semicolon1")
    semicolon2 = match.group("semicolon2")
    code1 = match.group("code1")
    code2 = match.group("code2")
    code3 = match.group("code3")

    def is_spacing_okay(semicolon, before_code, after_code):
        spacing_before = semicolon.startswith(" ")
        spacing_after = semicolon.endswith(" ")

        def check_spacing(convention, actual):
            if convention is None:
                convention = actual

            if convention != actual:
                return convention, False
            else:
                return convention, True

        if before_code or after_code:
            if before_code:
                self.for_loop_spacing_before, result = check_spacing(
                    self.for_loop_spacing_before,
                    spacing_before
                )
                if not result:
                    return False
            if after_code:
                self.for_loop_spacing_after, result = check_spacing(
                    self.for_loop_spacing_after,
                    spacing_after
                )
                if not result:
                    return False
        else:
            # This is a plain semicolon, so we can't infer anything about the
            # spacing convention.
            pass
        return True

    if not (
                is_spacing_okay(semicolon1, code1, code2)
            and is_spacing_okay(semicolon2, code2, code3)
    ):
        self.add_error(
            label="FOR_LOOP_SEMICOLON_SPACING",
            data={"line": self.current_line_num}
        )
