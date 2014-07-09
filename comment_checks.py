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

def check_line_width(self, line):
    max_length = 80
    current_length = len(line)
    if current_length > max_length:
        self.add_error(label="LINE_WIDTH", data={'length': current_length})

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
        self.add_error(label="MISSING_RME")
