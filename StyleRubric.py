from cpplint import RemoveMultiLineComments, CleansedLines, GetPreviousNonBlankLine
from style_grader_classes import DataStructureTracker, SpacingTracker
from style_grader_functions import check_if_function, get_arguments, check_operator_regex, check_if_break_statement, check_if_switch_statement
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, printables, srange
from StyleError import StyleError
from ConfigParser import ConfigParser
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

class StyleRubric(object):
    """
    This class sets all variable aspects of grading (whitespace, gotos etc)
    """
    def __init__(self):
        config = ConfigParser()
        config.read('rubric.ini')
        self.student_files = config.get('FILES', 'student_files').split(',')
        self.permitted_includes = config.get('FILES', 'permitted_includes').split(',')
        # A list of StyleError objects generated from student's code
        self.error_tracker = list()
        self.error_types = dict()
        self.total_errors = 0
        self.reset_for_new_file()

    def reset_for_new_file(self):
        self.spacer = SpacingTracker()
        self.outside_main = True
        self.egyptian = False
        self.notEgyptian = False
        self.braces_error = False #To prevent multiple braces errors
        self.in_switch = False

    def add_error(self, label, line=0, column=0, data={}):
        self.total_errors += 1
        if label not in self.error_types:
            self.error_types[label] = 0
        if not line:
            line = self.current_line_num + 1
        self.error_types[label] += 1
        self.error_tracker.append(StyleError(1, label, line, column_num=column, data=data))

    def grade_student_file(self, filename):
        print "Grading student submission: {}".format(filename)
        # This avoids getting the period character
        location = filename.find('.') + 1
        extension = filename[location:]
        if extension not in ['h', 'cpp']:
            sys.stderr.write("Incorrect file type\n")
            return
        cleaned_file = self.clean_file(filename)
        error = ""
        RemoveMultiLineComments(filename, cleaned_file, error)
        clean_lines = CleansedLines(cleaned_file)
        full_lines = open(filename, 'rU').readlines()
        code = clean_lines.lines
        for line_num in range(len(code)):
            self.current_line_num = line_num
            self.parse_current_line_of_code(clean_lines)
        for line_num in range(len(full_lines)):
            self.current_line_num = line_num
            self.parse_comments_for_line(full_lines)
        self.check_pointer_reference_consistency()
    
    def parse_current_line_of_code(self, clean_lines):
        code = clean_lines.lines[self.current_line_num]

        #Check for proper main() declaration (if main is present on this line)
        self.check_main_syntax(code)
        #Check non const globals
        self.check_non_const_global(code)
         #Only one statement on the return line?
        self.check_int_for_bool(code)
        #One statement per line
        self.check_statements_per_line(clean_lines)
        #check to see if the line contains a goto function
        self.check_goto(code)
        #Check for mixed tabs/spaces and log error #TODO: This can wait
        #Check for #define statements
        self.check_define_statement(code) 
        #Check for "== true" statements
        self.check_equals_true(code) 
        #Check for "while(true)" statements
        self.check_while_true(code) 
        #Check ternary expressions
        self.check_ternary_operator(code)
        #Check continue statements
        self.check_continue(code) 
        #Check stringstreams
        self.check_stringstream(code)
        #Check for unnecessary includes
        self.check_unnecessary_include(code)
        #Check for operator Spacing
        self.check_operator_spacing(code)
        #Check for capitalization of first character
        self.check_first_char(code)
        #Call function or checking INDENTATION!!
        self.check_block_indentation(clean_lines)
        #Check for braces being consistent (egyptian or non-egyptian)
        self.check_brace_consistency(clean_lines)
    
    def parse_comments_for_line(self, lines):
        text = lines[self.current_line_num]
        #Check line width
        self.check_line_width(text)
        #Check RMEs
        if check_if_function(text):
            self.check_missing_rme(lines)

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
                    self.add_error("INT_FOR_BOOL")

    def check_statements_per_line(self, clean_lines):
        cleansed_line = clean_lines.lines[self.current_line_num]
        # This code is taken directly from cpplint lines 3430-3440
        if (cleansed_line.count(';') > 1 and
           # for loops are allowed two ;'s (and may run over two lines).
           cleansed_line.find('for') == -1 and
           (GetPreviousNonBlankLine(clean_lines, self.current_line_num)[0].find('for') == -1 or
           GetPreviousNonBlankLine(clean_lines, self.current_line_num)[0].find(';') != -1) and
           # It's ok to have many commands in a switch case that fits in 1 line
           not ((cleansed_line.find('case ') != -1 or
           cleansed_line.find('default:') != -1) and
           cleansed_line.find('break;') != -1)):
            self.add_error("STATEMENTS_PER_LINE")

    def check_operator_spacing(self, code):
        # Check normal operators
        for operator in ['+', '-', '/', '%']:
            column_num = check_operator_regex(code, '\{}'.format(operator))
            if column_num:
                data = {'operator': operator}
                #self.add_error("OPERATOR_SPACING", column=column_num, data=data)
                self.add_error("OPERATOR_SPACING")
        # Check ampersands
        for match in re.findall('.&.', code):
            if '&' in [match[0], match[2]]:
                continue
            elif match[0] == ' ':
                if match[2] == ' ':
                    if self.spacer.amps_left or self.spacer.amps_right:
                        self.add_error('OPERATOR_CONSISTENCY')
                    self.spacer.amps_both = True
                else:
                    if self.spacer.amps_right or self.spacer.amps_both:
                        self.add_error('OPERATOR_CONSISTENCY')
                    self.spacer.amps_left = True
            else:
                if match[2] == ' ':
                    if self.spacer.amps_left or self.spacer.amps_both:
                        self.add_error('OPERATOR_CONSISTENCY')
                    self.spacer.amps_right = True
        # Check asterisks
        for match in re.findall('.\*+.', code):
            if match[0] == ' ' and match[-1] != ' ':
                if self.spacer.asts_right:
                    self.add_error('OPERATOR_CONSISTENCY')
                self.spacer.asts_left = True
            elif match[0] != ' ' and match[-1] == ' ':
                if self.spacer.asts_left:
                    self.add_error('OPERATOR_CONSISTENCY')
                self.spacer.asts_right = True

    def check_pointer_reference_consistency(self):
        if self.spacer.asts_left:
            if self.spacer.amps_right or self.spacer.amps_both:
                self.add_error('POINTER_REFERENCE_CONSISTENCY')
        elif self.spacer.asts_right:
            if self.spacer.amps_left or self.spacer.amps_both:
                self.add_error('POINTER_REFERENCE_CONSISTENCY')

    def check_equals_true(self, code):
        variable = Word(alphanums)
        keyword = Literal("true") | Literal("false")
        statement_parser = Group(variable + "==" + keyword) | Group(keyword + "==" + variable)
        if len(statement_parser.searchString(code)):
            self.add_error("EQUALS_TRUE") 

    def check_goto(self, code):
        match = Literal("goto")
        if len(match.searchString(code)):
            self.add_error("GOTO")

    def check_define_statement(self, code):
        match = Literal("#")+Literal("define")
        if len(match.searchString(code)):
            self.add_error("DEFINE_STATEMENT")

    def check_stringstream(self, code):
        match = Literal("#")+Literal("include")+Literal("<sstream>")
        try: result = match.parseString(code)
        except ParseException: pass
        else: self.add_error("STRINGSTREAM")

    def check_continue(self, code):
        quotedContinue = '"'+SkipTo(Literal("continue"))+"continue"+SkipTo(Literal('"'))+'"'
        if len(Literal("continue").searchString(code)) and not len(quotedContinue.searchString(code)):
            self.add_error("CONTINUE_STATEMENT")

    def check_ternary_operator(self, code):
        # This is really easy - ternary operators require the conditional operator "?",
        # which has no other application in C++. Since we're parsing out comments, it's as easy as:
        quotedTernary = '"'+SkipTo(Literal("?"))+"?"+SkipTo(Literal('"'))+'"'
        if len(Literal("?").searchString(code)) and not len(quotedTernary.searchString(code)):
            self.add_error("TERNARY_OPERATOR")

    def check_while_true(self, code):
        statement_parser = Literal("while") + Literal("(") + Literal("true") + Literal(")")
        if len(statement_parser.searchString(code)):
            self.add_error("WHILE_TRUE")

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
                self.add_error("NON_CONST_GLOBAL")

    def set_egyptian_style(self, egyptian_bool):
        if egyptian_bool: self.egyptian = True
        else: self.notEgyptian = True

    def check_brace_consistency(self, clean_lines):
        code = clean_lines.lines[self.current_line_num]
        stripped_code = code.strip()
        function = check_if_function(code)
        if_statement = re.search(r'^if\s*\(\s*', stripped_code)
        else_if_statement = re.search(r'^else\s*\(', code)
        else_statement = re.search(r'^else\s+', code)
        switch_statement = re.search(r'^switch\s*\(', stripped_code)
        #TODO: Clean this line up

        if function or if_statement or else_statement or switch_statement:
            if function and clean_lines.lines[self.current_line_num + 1].find('{') != -1 or\
                else_if_statement and clean_lines.lines[self.current_line_num + 1].find('{') != -1 or\
                else_statement and clean_lines.lines[self.current_line_num + 1].find('{') != -1 or\
                switch_statement and clean_lines.lines[self.current_line_num + 1].find('{') != -1 or\
                    if_statement and clean_lines.lines[self.current_line_num + 1].find('{') != -1:

                self.set_egyptian_style(False)
            elif function and code.find('{') != -1 or \
                    else_if_statement and code.find('{') != -1 or\
                    else_statement and code.find('{') != -1 or\
                    switch_statement and code.find('{') != -1 or\
                    if_statement and code.find('{') != -1:

                self.set_egyptian_style(True)
            elif not self.outside_main:
                if not self.braces_error:
                    self.add_error("BRACE_CONSISTENCY")
                    self.braces_error = True

            #if both of these are true, they are not consistent, therefore error.
            if self.notEgyptian:
                if self.egyptian and not self.braces_error:
                    self.add_error("BRACE_CONSISTENCY")
                    self.braces_error = True

    def check_block_indentation(self, clean_lines):
        #TODO: Load from config file? 
        tab_size = 4
        code = clean_lines.lines[self.current_line_num]
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
        if function or self.outside_main:
            if indentation_size != 0:
                data = {'expected': 0, 'found': indentation_size}
                #self.add_error("BLOCK_INDENTATION", data=data)
                self.add_error("BLOCK_INDENTATION")
            if self.outside_main:
                return
        #TODO: Need to check indentation ON the same line as the function still
        if function:
            #if not egyptian style
            if code.find('{') == -1:
                second_line = clean_lines.lines[self.current_line_num + 1]
                if code.find('{'):
                    temp_line_num = self.current_line_num + 1
                    data_structure_tracker = DataStructureTracker()
                    data_structure_tracker.brace_stack.append('{')
                    self.process_current_blocks_indentation(indentation, tab_size, code,
                                                            clean_lines, data_structure_tracker,
                                                            temp_line_num)
                else:
                    #TODO Figure out what it means to not have braces in the right place
                    pass
            else:
                temp_line_num = self.current_line_num
                data_structure_tracker = DataStructureTracker()
                data_structure_tracker.brace_stack.append('{')
                self.process_current_blocks_indentation(indentation, tab_size, code,
                                                        clean_lines, data_structure_tracker,
                                                        temp_line_num)
        else:
            return

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
                self.add_error("MAIN_SYNTAX")

    def check_first_char(self, code):
        # check if the first char is lower-case alpha or '_'
        identifier_name = Word(srange("[a-z]") + "_", alphanums + "_")
        keywords = ("struct", "class")
        for keyword in keywords:
            syntax = Literal(keyword) + identifier_name
            parsed = syntax.searchString(code).asList()
            if len(parsed):
                '''
                self.add_error("FIRST_CHAR",
                               data={"keyword": keyword,
                                     "expected": str(parsed[0][1]).capitalize(),
                                     "found": str(parsed[0][1])})
                '''
                self.add_error("FIRST_CHAR")
                return

    def process_current_blocks_indentation(self, indentation, tab_size, code, clean_lines,
                                           data_structure_tracker, temp_line_num):
        indentation = re.search(r'^( *)\S', clean_lines.lines[temp_line_num])
        indentation = indentation.group()
        indentation_size = len(indentation) - len(indentation.strip())
        data_structure_tracker.in_block = True
        next_indentation = indentation_size + tab_size
        while data_structure_tracker.in_block:
            temp_line_num += 1
            current_indentation = re.search(r'^( *)\S',
                                            clean_lines.lines[temp_line_num])
            switch_statement = check_if_switch_statement(clean_lines.lines[temp_line_num])
            if(switch_statement):
                data_structure_tracker.in_switch = True
            is_break_statement = check_if_break_statement(clean_lines.lines[temp_line_num])
            if is_break_statement and not data_structure_tracker.in_switch:
                #self.add_error("UNNECESSARY_BREAK", line=temp_line_num + 1)
                self.add_error("UNNECESSARY_BREAK")
            if current_indentation:
                line_start = current_indentation.group()
                current_indentation = len(line_start) - len(line_start.strip())
                if current_indentation != next_indentation and line_start.find('}') == -1:
                    data = {'expected': next_indentation, 'found': current_indentation}
                    #self.add_error("BLOCK_INDENTATION", temp_line_num + 1, data=data)
                    self.add_error("BLOCK_INDENTATION")
                if clean_lines.lines[temp_line_num].find("{") != -1:
                    if data_structure_tracker.in_switch:
                        data_structure_tracker.add_switch_brace("{")
                    data_structure_tracker.add_brace("{")
                    next_indentation = current_indentation + tab_size
                elif clean_lines.lines[temp_line_num].find("}") != -1:
                    if data_structure_tracker.in_switch:
                        data_structure_tracker.pop_switch_brace()
                    data_structure_tracker.pop_brace()
                    next_indentation = next_indentation - tab_size

    def check_unnecessary_include(self, code):
        grammar = Literal('#') + Literal('include') + Literal('<') + Word(alphanums)
        try:
            grammar.parseString(code)
            begin = code.find("<")
            end = code.find(">")
            included_library = code[begin + 1:end]
            if included_library not in self.permitted_includes:
                self.add_error("UNNECESSARY_INCLUDE")
        except ParseException:
            return

    def check_line_width(self, line):
        max_length = 80
        current_length = len(line)
        if current_length > max_length:
            #self.add_error("LINE_WIDTH", data={'length': current_length})
            self.add_error("LINE_WIDTH")

    def check_missing_rme(self, lines):
        requires = effects = modifies = False
        #Check if there's a complete RME in the last 10 lines
        for line_num in range(self.current_line_num - 10, self.current_line_num):
            code = lines[line_num].lower()
            if re.search('requires', code): requires = True
            if re.search('effects', code): effects = True
            if re.search('modifies', code): modifies = True
        # If it's not there, maybe they defined it in a header file. Finish this once headers are saved
        if not (requires and effects and modifies):
            self.add_error("MISSING_RME")

    def clean_file(self, filename):
        try:
            dirty_text = codecs.open(filename, 'r', 'utf8', 'replace').read().split('\n')
            newline = False
            ending = ''
            for x in range(0, len(dirty_text)):
                if len(dirty_text[x]) > 0:
                    ending = dirty_text[x][-1]
                if ending == '\r':
                    dirty_text[x] = dirty_text[x].rstrip('\r')
                    newline = True
                else:
                    newline = False

        except IOError:
            sys.stderr.write(
                "This file could not be read: '%s.'  "
                "Please check filename and resubmit \n" % filename)
        return dirty_text
