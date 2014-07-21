'''
Style Grader class with instance-method plugin-based functionality.
'''

import codecs
from ConfigParser import ConfigParser
from collections import defaultdict
import sys

from cpplint import CleansedLines, RemoveMultiLineComments

from style_grader_functions import check_if_function, print_success
from style_grader_classes import SpacingTracker
from StyleError import StyleError
import comment_checks
import multi_line_checks
import misc_checks
import single_line_checks

def safely_open(filename):
    try:
        dirty_text = codecs.open(filename, 'r', 'utf8', 'replace').readlines()
        for num, line in enumerate(dirty_text):
            dirty_text[num] = line.rstrip('\r')
        return dirty_text
    except IOError:
        sys.stderr.write('This file could not be read: "%s."  '
                         'Please check filename and resubmit \n' % filename)

class StyleRubric(object):
    '''
    A style grader to generate StyleErrors from a list of C++ files.
    '''
    def __init__(self):
        ''' Load functionality based on config file specifications '''
        self.config = ConfigParser()
        self.config.read('rubric.ini')
        self.error_tracker = dict()
        self.error_types = defaultdict(int)
        self.total_errors = 0
        self.student_files = self.config.get('FILES', 'student_files').split(',')
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
        self.global_in_object = False;
        self.global_object_braces = []
        self.global_in_object_index = 0
        self.file_has_a_main = {}


    def add_global_brace(self, brace):
        self.global_object_braces.append(brace)
        self.global_in_object_index += 1

    def pop_global_brace(self):
        self.global_object_braces.pop()
        if self.global_in_object_index == 0:
            self.global_in_object = False

    def load_functions(self, module):
        functions = list()
        group = module.__name__.upper()
        for check in self.config.options(group):
            if self.config.get(group, check).lower() == 'yes':
                functions.append(getattr(module, 'check_'+check))
        return functions

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
        self.reset_for_new_file(filename)
        data = safely_open(filename)
        raw_data = safely_open(filename)
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
        # adjust missing RME error if RME is in a #included header file
        self.adjust_missing_rme()
        self.adjust_definitions_above_main()

    def adjust_missing_rme(self):
        for filename in self.missing_rme.iterkeys():
            extension = filename.split('.')[-1]
            if extension == 'cpp':
                name = filename.split('.')[0]
                full_header_filename = name + '.h'
                short_header_filename = full_header_filename.split('/')[-1]

                # check if header is #included
                if short_header_filename in self.local_includes[filename]:
                    for missing_rme in self.missing_rme[filename]:
                        if missing_rme in self.all_rme.get(full_header_filename):
                            for error in self.error_tracker[filename]:
                                if error.message == error.get_error_message('MISSING_RME') and \
                                    error.get_data().get('function_signature') == missing_rme:
                                    self.error_types['MISSING_RME'] -= 1
                                    self.total_errors -= 1
                                    self.error_tracker[filename].remove(error)

    def adjust_definitions_above_main(self):
        for filename in self.error_tracker.iterkeys():
            if not self.file_has_a_main[filename]:
                # remove error
                errors_to_keep = list()
                for error in self.error_tracker[filename]:
                    if error.message == error.get_error_message('DEFINITION_ABOVE_MAIN'):
                        self.error_types['DEFINITION_ABOVE_MAIN'] -= 1
                        self.total_errors -= 1
                    else:
                        errors_to_keep.append(error)
                self.error_tracker[filename] = errors_to_keep


    def print_errors(self):
        for filename, errors in self.error_tracker.iteritems():
            print 'Grading {}...'.format(filename)
            if not len(errors):
                print_success()
            for error in errors:
                print error
            print
