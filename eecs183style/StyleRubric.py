'''
Style Grader class with instance-method plugin-based functionality.
'''

import codecs
from ConfigParser import ConfigParser
from collections import defaultdict
import os
import sys
from copy import deepcopy
from glob import glob

from cpplint.cpplint import CleansedLines, RemoveMultiLineComments

from style_grader_functions import check_if_function, print_success, get_indent_level
from style_grader_classes import SpacingTracker
from StyleError import StyleError
import comment_checks
import multi_line_checks
import misc_checks
import single_line_checks
import adjustments

LOCAL_DIR = os.getcwd()

def safely_open(filename):
    try:
        dirty_text = codecs.open(filename, 'r', 'utf8', 'replace').readlines()
        for num, line in enumerate(dirty_text):
            dirty_text[num] = line.rstrip('\r')
        return dirty_text
    except IOError:
        sys.stderr.write('This file could not be read: "%s."  '
                         'Please check filename and resubmit \n' % filename)
        return

class StyleRubric(object):
    '''
    A style grader to generate StyleErrors from a list of C++ files.
    '''
    def __init__(self, student_files=None):
        ''' Load functionality based on config file specifications '''
        self.config = ConfigParser()
        self.config.read(LOCAL_DIR+'/rubric.ini')
        self.error_tracker = dict()
        self.error_types = defaultdict(int)
        self.total_errors = 0
        self.includes = self.config.get('FILES', 'permitted_includes').split(',')
        self.local_includes = dict()
        self.all_rme = dict()
        self.missing_rme = dict()
        self.min_comments_ratio = float(self.config.get('SETTINGS', 'min_comments_ratio'))
        self.max_line_length = int(self.config.get('SETTINGS', 'max_line_length'))
        self.single_line_checks = self.load_functions(single_line_checks)
        self.multi_line_checks = self.load_functions(multi_line_checks)
        self.comment_checks = self.load_functions(comment_checks)
        self.misc_checks = self.load_functions(misc_checks)
        self.adjustments = self.load_functions(adjustments, prefix='adjust')
        self.global_in_object = False;
        self.global_object_braces = []
        self.global_in_object_index = 0
        self.file_has_a_main = {}
        self.current_file_indentation = 4

        if student_files:
            self.student_files = student_files
        else:
            self.student_files = self.load_filenames(self.config.get('FILES', 'student_files').split(','))


    def add_global_brace(self, brace):
        self.global_object_braces.append(brace)
        self.global_in_object_index += 1

    def pop_global_brace(self):
        self.global_object_braces.pop()
        if self.global_in_object_index == 0:
            self.global_in_object = False

    def load_functions(self, module, prefix='check'):
        functions = list()
        group = module.__name__.split('.')[-1].upper()
        for check in self.config.options(group):
            if self.config.get(group, check).lower() == 'yes':
                functions.append(getattr(module, prefix + '_' + check))
        return functions

    def load_filenames(self, paths):
        all_files = list()
        for path in paths:
            files = glob(path)
            all_files.extend(files)
        return all_files

    def reset_for_new_file(self, filename):
        self.spacer = SpacingTracker()
        self.outside_main = True
        self.egyptian = False
        self.not_egyptian = False
        self.braces_error = False #To prevent multiple braces errors
        self.in_switch = False
        self.current_file = filename
        self.error_tracker[filename] = list()
        self.all_rme[filename] = set()
        self.missing_rme[filename] = set()
        self.local_includes[filename] = list()
        self.current_file_indentation = get_indent_level(open(filename, 'rU'))

    def add_error(self, label=None, line=-1, column=0, type='ERROR', data=dict()):
        self.total_errors += 1
        self.error_types[label] += 1
        line = line if (line != -1) else self.current_line_num + 1
        self.error_tracker[self.current_file].append(StyleError(1, label, line, column_num=column, type=type, data=data))

    def grade_student_file(self, filename):
        extension = filename.split('.')[-1]
        if extension not in ['h', 'cpp']:
            sys.stderr.write('Failed to parse {}: incorrect file type.\n'.format(filename))
            return
        data = safely_open(filename)
        if data:
            self.reset_for_new_file(filename)
            raw_data = deepcopy(data)
            RemoveMultiLineComments(filename, data, '')
            clean_lines = CleansedLines(data)
            clean_code = clean_lines.lines
            for self.current_line_num, code in enumerate(clean_code):
                for function in self.single_line_checks: function(self, code)
                for function in self.multi_line_checks: function(self, clean_lines)
            # COMMENT CHECKS #TODO
            for self.current_line_num, text in enumerate(raw_data):
                if self.config.get('COMMENT_CHECKS', 'line_width').lower() == 'yes':
                    getattr(comment_checks, 'check_line_width')(self, text)
                if check_if_function(text):
                    if self.config.get('COMMENT_CHECKS', 'missing_rme').lower() == 'yes':
                        getattr(comment_checks, 'check_missing_rme')(self, raw_data)
            if self.config.get('COMMENT_CHECKS', 'min_comments').lower() == 'yes':
                getattr(comment_checks, 'check_min_comments')(self, raw_data, clean_code)
            for function in self.misc_checks: function(self)
            self.error_tracker[filename].sort()
            self.file_has_a_main[filename] = not self.outside_main

    def adjust_errors(self):
        for function in self.adjustments:
            function(self)

    def print_errors(self):
        for filename, errors in self.error_tracker.iteritems():
            print 'Grading {}...'.format(filename)
            if not len(errors):
                print_success()
            for error in errors:
                print error
            print
