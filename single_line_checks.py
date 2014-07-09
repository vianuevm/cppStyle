from style_grader_functions import check_if_function, check_operator_regex
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, srange
import re

def check_int_for_bool(self, code):
    returnVal = Literal("return")
    if len(returnVal.searchString(code)): 
       # make sure it's not the end of a word
        list_of_line = code.split(' ')
        if len(list_of_line) > 2:
            #TODO Figure out what you want to take off with a more than one statement on return line
            pass
        else:
            code = code[6:].strip()
            if code.isdigit():
                self.add_error(label="INT_FOR_BOOL")

def check_operator_spacing(self, code):
    # Check normal operators
    for operator in ['+', '-', '/', '%']:
        column_num = check_operator_regex(code, '\{}'.format(operator))
        if column_num:
            data = {'operator': operator}
            self.add_error(label="OPERATOR_SPACING", column=column_num, data=data)
    # Check ampersands
    for match in re.findall('.&.', code):
        if '&' in [match[0], match[2]]:
            continue
        elif match[0] == ' ':
            if match[2] == ' ':
                if self.spacer.amps_left or self.spacer.amps_right:
                    self.add_error(label='OPERATOR_CONSISTENCY')
                self.spacer.amps_both = True
            else:
                if self.spacer.amps_right or self.spacer.amps_both:
                    self.add_error(label='OPERATOR_CONSISTENCY')
                self.spacer.amps_left = True
        else:
            if match[2] == ' ':
                if self.spacer.amps_left or self.spacer.amps_both:
                    self.add_error(label='OPERATOR_CONSISTENCY')
                self.spacer.amps_right = True
    # Check asterisks
    for match in re.findall('.\*+.', code):
        if match[0] == ' ' and match[-1] != ' ':
            if self.spacer.asts_right:
                self.add_error(label='OPERATOR_CONSISTENCY')
            self.spacer.asts_left = True
        elif match[0] != ' ' and match[-1] == ' ':
            if self.spacer.asts_left:
                self.add_error(label='OPERATOR_CONSISTENCY')
            self.spacer.asts_right = True

def check_equals_true(self, code):
    variable = Word(alphanums)
    keyword = Literal("true") | Literal("false")
    statement_parser = Group(variable + "==" + keyword) | Group(keyword + "==" + variable)
    if len(statement_parser.searchString(code)):
        self.add_error(label="EQUALS_TRUE") 

def check_goto(self, code):
    match = Literal("goto")
    if len(match.searchString(code)):
        self.add_error(label="GOTO")

def check_define_statement(self, code):
    match = Literal("#")+Literal("define")
    if len(match.searchString(code)):
        self.add_error(label="DEFINE_STATEMENT")

def check_stringstream(self, code):
    match = Literal("#")+Literal("include")+Literal("<sstream>")
    try: match.parseString(code)
    except ParseException: pass
    else: self.add_error(label="STRINGSTREAM")

def check_continue(self, code):
    quoted_continue = '"'+SkipTo(Literal("continue"))+"continue"+SkipTo(Literal('"'))+'"'
    if len(Literal("continue").searchString(code)) and not len(quoted_continue.searchString(code)):
        self.add_error(label="CONTINUE_STATEMENT")

def check_ternary_operator(self, code):
    # This is really easy - ternary operators require the conditional operator "?",
    # which has no other application in C++. Since we're parsing out comments, it's as easy as:
    quoted_ternary = '"'+SkipTo(Literal("?"))+"?"+SkipTo(Literal('"'))+'"'
    if len(Literal("?").searchString(code)) and not len(quoted_ternary.searchString(code)):
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
        variable = LineStart()+Word(alphanums+"_")+Word(alphanums+"_")
        special_keywords = LineStart()+Literal("using") | LineStart()+Literal("class") | LineStart()+Literal("struct")
        constant = LineStart()+Optional("static")+Literal("const")
        if not function and len(variable.searchString(code)) and \
           not len(special_keywords.searchString(code)) and \
           not len(constant.searchString(code)):
            self.add_error(label="NON_CONST_GLOBAL")


def check_main_syntax(self, code):
    #Return value for main is optional in C++11
    parser = Literal("int")+Literal("main")+Literal("(")+SkipTo(Literal(")"))+Literal(")")
    if len(parser.searchString(code)):
        main_prefix = Literal("main")+Literal("(")
        full_use = Literal("int")+"argc"+","+Optional("const")+"char"+"*"+"argv"+"["+"]"+")"
        # 3 options for main() syntax
        if not len((main_prefix+Literal(")")).searchString(code)) and \
           not len((main_prefix+Literal("void")+Literal(")")).searchString(code)) and \
           not len((main_prefix+full_use).searchString(code)):
            self.add_error(label="MAIN_SYNTAX")

def check_first_char(self, code):
    # check if the first char is lower-case alpha or '_'
    identifier_name = Word(srange("[a-z]") + "_", alphanums + "_")
    keywords = ("struct", "class")
    for keyword in keywords:
        syntax = Literal(keyword) + identifier_name
        parsed = syntax.searchString(code).asList()
        if len(parsed):
            self.add_error(label="FIRST_CHAR",
                           data={"keyword": keyword,
                                 "expected": str(parsed[0][1]).capitalize(),
                                 "found": str(parsed[0][1])})
            return


def check_unnecessary_include(self, code):
    grammar = Literal('#') + Literal('include') + Literal('<') + Word(alphanums)
    try:
        grammar.parseString(code)
        begin = code.find("<")
        end = code.find(">")
        included_library = code[begin + 1:end]
        if included_library not in self.permitted_includes:
            self.add_error(label="UNNECESSARY_INCLUDE")
    except ParseException:
        return

