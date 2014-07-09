from cpplint import RemoveMultiLineComments, CleansedLines, GetPreviousNonBlankLine
from style_grader_classes import DataStructureTracker, SpacingTracker
from style_grader_functions import check_if_function, get_arguments, check_operator_regex, check_if_break_statement, check_if_switch_statement, indent_helper
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
        self.add_error(label="STATEMENTS_PER_LINE")

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

            self.notEgyptian = True
        elif function and code.find('{') != -1 or \
                else_if_statement and code.find('{') != -1 or\
                else_statement and code.find('{') != -1 or\
                switch_statement and code.find('{') != -1 or\
                if_statement and code.find('{') != -1:

            self.egyptian = True
        elif not self.outside_main:
            if not self.braces_error:
                self.add_error(label="BRACE_CONSISTENCY")
                self.braces_error = True

        #if both of these are true, they are not consistent, therefore error.
        if self.notEgyptian:
            if self.egyptian and not self.braces_error:
                self.add_error(label="BRACE_CONSISTENCY")
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
            self.add_error(label="BLOCK_INDENTATION", data=data)
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
                results = indent_helper(indentation, tab_size, code, clean_lines, 
                                        data_structure_tracker, temp_line_num)
                for error in results:
                    self.add_error(**error)
            else:
                #TODO Figure out what it means to not have braces in the right place
                pass
        else:
            temp_line_num = self.current_line_num
            data_structure_tracker = DataStructureTracker()
            data_structure_tracker.brace_stack.append('{')
            results = indent_helper(indentation, tab_size, code, clean_lines, 
                                    data_structure_tracker, temp_line_num)
            for error in results:
                self.add_error(**error)
    else:
        return
