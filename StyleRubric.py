from cpplint import RemoveMultiLineComments, CleansedLines, GetPreviousNonBlankLine
from style_grader_classes import DefaultFilters, DataStructureTracker, OperatorSpace
from style_grader_functions import check_if_function, get_arguments, check_operator_regex
from pyparsing import Literal, Word, Optional, ParseException, Group, SkipTo, alphanums, LineStart, printables
from StyleError import StyleError
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
        self.total_errors = 0
        self.filters = DefaultFilters()
        self.error_types = {}
        # A list of StyleError objects generated from student's code
        self.error_tracker = []
        self.output_format = "emacs" #TODO: If this can be something other than 'emacs', should load from config file
        self.reset_for_new_file()
        self.braces_error = False #To prevent multiple braces errors

    def reset_for_new_file(self):
        self.outside_main = True
        self.egyptian = False
        self.notEgyptian = False

    def set_total_errors(self, errors): 
        #NOTE: Potential issue if total_errors does not match count held by self.error_types. Might be fine, haven't read all yet
        self.total_errors = errors

    def set_filters(self, filters): #TODO: You are going to need to figure out what this will do and how
        self.filters = filters

    def set_output_format(self, format):
        self.output_format = format

    def reset_error_count(self):
        self.total_errors = 0
        self.error_types = {}

    def set_inside_main(self):
        self.outside_main = False

    def is_outside_main(self):
        return self.outside_main

    def add_error(self, label):
        #Naming convention adds clarity
        self.total_errors += 1
        if label not in self.error_types:
            self.error_types[label] = 0

        self.error_types[label] += 1
        self.error_tracker.append(StyleError(1, label, self.current_line_num))

    def set_egyptian_style(self, egyptian_bool):
        if egyptian_bool:
            self.egyptian = True
        else:
            self.notEgyptian = True

    def valid_return(self, code):
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
                    self.add_error("BOOL_VALUE")

    def num_of_commands(self, clean_lines):
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
            
            self.add_error("COMMAND_ERROR")
        
    def line_width_check(self, line):
        max_length = 80
        current_length = len(line)
        if current_length > max_length:
            self.add_error("LINE_WIDTH")

    def operator_spacing(self, code, operator_space_tracker):
        #TODO: Why is operator_space_tracker passed to this fn but not used
        if not check_operator_regex(code, '\+')  or \
            not check_operator_regex(code, '\-') or \
            not check_operator_regex(code, '\/') or \
            not check_operator_regex(code, '\%') or \
            not check_operator_regex(code, '\*'):
            self.add_error("OPERATOR_SPACE_ERROR")
            return False

        else:
            return True

    def check_equals_true(self, code):
        variable = Word(alphanums)
        keyword = Literal("true") | Literal("false")
        statement_parser = Group(variable + "==" + keyword) | Group(keyword + "==" + variable)
        if len(statement_parser.searchString(code)):
            self.add_error("EQUALS_TRUE") 

    def check_go_to(self, code):
        match = Literal("goto")
        if len(match.searchString(code)):
            self.add_error("GOTO")

    def check_define_statements(self, code):
        match = Literal("#")+Literal("define")
        if len(match.searchString(code)):
            self.add_error("DEFINE_STATEMENT")

    def check_for_stringstreams(self, code):
        match = Literal("#")+Literal("include")+Literal("<sstream>")
        try:
            result = match.parseString(code)
            self.add_error("STRINGSTREAM")
        except ParseException:
            pass

    def check_continue_statements(self, code):
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
            self.set_inside_main()

        if self.is_outside_main():
            function = check_if_function(code)
            variable = LineStart()+Word(alphanums+"_")+Word(alphanums+"_")
            using = LineStart()+Literal("using")
            if not function and len(variable.searchString(code)) and not len(using.searchString(code)):
                self.add_error("GLOBAL_VARIABLE")

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
            elif not self.is_outside_main():
                if not self.braces_error:
                    self.add_error("BRACES_ERROR")
                    self.braces_error = True

            #if both of these are true, they are not consistent, therefore error.
            if self.notEgyptian:
                if self.egyptian and not self.braces_error:
                    self.add_error("BRACES_ERROR")
                    self.braces_error = True

    def check_function_block_indentation(self, clean_lines, operator_space_tracker):
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

        if function or self.is_outside_main():
            if indentation_size != 0:
                self.add_error("INDENTATION_ERROR")
            if self.is_outside_main():
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

    def check_main_prefix(self, code):
        #Return value for main is optional in C++11
        parser = Literal("int")+Literal("main")+Literal("(")+SkipTo(Literal(")"))+Literal(")")
        if len(parser.searchString(code)):
            main_prefix = Literal("main")+Literal("(")
            full_use = Literal("int")+"argc"+","+"char"+"*"+"argv"+"["+"]"+")"
            # 3 options for main() syntax
            if not len((main_prefix+Literal(")")).searchString(code)) and \
               not len((main_prefix+Literal("void")+Literal(")")).searchString(code)) and \
               not len((main_prefix+full_use).searchString(code)):
                self.add_error("MAIN_SYNTAX")

    def process_current_blocks_indentation(self, indentation, tab_size, code, clean_lines,
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
                    self.add_error("INDENTATION_ERROR", temp_line_num)
                if clean_lines.lines[temp_line_num].find("{") != -1:
                    data_structure_tracker.add_brace("{")
                    next_indentation = current_indentation + tab_size
                elif clean_lines.lines[temp_line_num].find("}") != -1:
                    data_structure_tracker.pop_brace()
                    next_indentation = next_indentation - tab_size

    def parse_current_line_of_code(self, clean_lines, operator_space_tracker):
        code = clean_lines.lines[self.current_line_num]
        #Check for proper main() declaration (if main is present on this line)
        self.check_main_prefix(code)
        #Check non const globals
        self.check_non_const_global(code)
         #Only one statement on the return line?
        self.valid_return(code)
        #One statement per line
        self.num_of_commands(clean_lines)
        #check to see if the line contains a goto function
        self.check_go_to(code)
        #Check for mixed tabs/spaces and log error #TODO: This can wait
        #Check line width
        self.line_width_check(code)
        #Check for #define statements
        self.check_define_statements(code) 
        #Check for "== true" statements
        self.check_equals_true(code) 
        #Check for "while(true)" statements
        self.check_while_true(code) 
        #Check ternary expressions
        self.check_ternary_operator(code)
        #Check continue statements
        self.check_continue_statements(code) 
        #Check stringstreams
        self.check_for_stringstreams(code)
        
        #Check for unnecessary includes
        #TODO: Above duh.

        #Check for operator Spacing
        self.operator_spacing(code, operator_space_tracker)

        #Call function or checking INDENTATION!!
        self.check_function_block_indentation(clean_lines, operator_space_tracker)
        #TODO THIS IS UNDER CONSTRUCTION
        #Check for braces being consistent (egyptian or non-egyptian)
        self.check_brace_consistency(clean_lines)

    def grade_student_file(self, filename, operator_space_tracker):
        print "Grading student submission: {}".format(filename)
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
                sys.stderr.write("Incorrect file type\n")
                return
        except IOError:
            sys.stderr.write(
                "This file could not be read: '%s.'  "
                "Please check filename and resubmit \n" % filename)
        else:
            error = ""
            RemoveMultiLineComments(filename, student_code, error)
            clean_lines = CleansedLines(student_code)
            code = clean_lines.lines
            for line_num in range(len(code)):
                self.current_line_num = line_num
                self.parse_current_line_of_code(clean_lines, operator_space_tracker)
