from configparser import ConfigParser
import codecs
import os
import sys
from cpplint import RemoveMultiLineComments, CleansedLines
from style_grader_classes import SpacingTracker
from style_grader_functions import check_if_function
from StyleError import StyleError
import single_line_checks
import multi_line_checks
import comment_checks
import misc_checks

class StyleRubric(object):
    """
    A style grader to generate StyleErrors into self.error_tracker from a list of C++ files.
    """
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('rubric.ini')
        self.student_files = self.config.get('FILES', 'student_files').split(',')
        self.permitted_includes = self.config.get('FILES', 'permitted_includes').split(',')

        self.single_line_checks = self.load_functions(single_line_checks)
        self.multi_line_checks = self.load_functions(multi_line_checks)
        self.comment_checks = self.load_functions(comment_checks)
        self.misc_checks = self.load_functions(misc_checks)

        # A list of StyleError objects generated from student's code
        self.error_tracker = list()
        self.error_types = dict()
        self.total_errors = 0
    
    def load_functions(self, module):
        functions = list()
        group = module.__name__.upper()
        for check in self.config[group]:
            if self.config[group][check].lower() == 'yes':
                functions.append(getattr(module, 'check_'+check))
        return functions

    def reset_for_new_file(self):
        self.spacer = SpacingTracker()
        self.outside_main = True
        self.egyptian = False
        self.notEgyptian = False
        self.braces_error = False #To prevent multiple braces errors
        self.in_switch = False

    def add_error(self, label=None, line=0, column=0, data=dict()):
        self.total_errors += 1
        if label not in self.error_types:
            self.error_types[label] = 0
        if not line:
            line = self.current_line_num + 1
        self.error_types[label] += 1
        self.error_tracker.append(StyleError(1, label, line, column_num=column, data=data))

    def grade_student_file(self, filename):
        self.reset_for_new_file()
        print "Grading student submission: {}".format(filename)
        extension = filename.split('.')[-1]
        if extension not in ['h', 'cpp']:
            sys.stderr.write("Incorrect file type\n")
            return
        cleaned_file = self.clean_file(filename)
        RemoveMultiLineComments(filename, cleaned_file, '')
        clean_lines = CleansedLines(cleaned_file)
        full_lines = open(filename, 'rU').readlines()
        code = clean_lines.lines
        for self.current_line_num, code in enumerate(code):
            # SINGLE LINE CHECKS
            for function in self.single_line_checks:
                function(self, code)
            # MULTI LINE CHECKS
            for function in self.multi_line_checks:
                function(self, clean_lines)
        # COMMENT CHECKS #TODO
        for self.current_line_num, text in enumerate(full_lines):
            if self.config['COMMENT_CHECKS']['line_width'] == 'yes':
                getattr(comment_checks, 'check_line_width')(self, text)
            if check_if_function(text):
                if self.config['COMMENT_CHECKS']['missing_rme'] == 'yes':
                    getattr(comment_checks, 'check_missing_rme')(self, full_lines)
        # MISC CHECKS #TODO
        if self.config['MISC_CHECKS']['pointer_reference_consistency'] == 'yes':
            getattr(misc_checks, 'check_pointer_reference_consistency')(self)

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
