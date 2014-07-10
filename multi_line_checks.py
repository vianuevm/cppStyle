from cpplint import GetPreviousNonBlankLine
from style_grader_classes import DataStructureTracker
from style_grader_functions import check_if_function,  indent_helper, check_if_struct_or_class
import re

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

            self.not_egyptian = True
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
        if self.not_egyptian:
            if self.egyptian and not self.braces_error:
                self.add_error(label="BRACE_CONSISTENCY")
                self.braces_error = True

def check_block_indentation(self, clean_lines):
    #TODO: Load from config file? 
    tab_size = 4
    code = clean_lines.lines[self.current_line_num]

    if check_if_struct_or_class(code):
        self.global_in_object = True

    if self.global_in_object and code.find('{') != -1:
        self.add_global_brace('{')
    elif self.global_in_object and code.find('}') != -1:
        self.pop_global_brace()

    function = check_if_function(code)
    struct_or_class = check_if_struct_or_class(code)
    indentation = re.search(r'^( *)\S', code)
    if indentation:
        indentation = indentation.group()
        indentation_size = len(indentation) - len(indentation.strip())
    else:
        return

    if function and indentation_size != 0 and not self.global_in_object:
        data = {'expected': 0, 'found': indentation_size}
        self.add_error(label="BLOCK_INDENTATION", data=data)

    #TODO: Need to check indentation ON the same line as the function still
    if (function and not self.outside_main) or struct_or_class:
        #if not egyptian style
        if code.find('{') == -1:
            if code.find('{'):
                temp_line_num = self.current_line_num + 1
                data_structure_tracker = DataStructureTracker()
                data_structure_tracker.brace_stack.append('{')
                if check_if_struct_or_class(code):
                    data_structure_tracker.in_class_or_struct = True
                if self.global_in_object:
                    self.add_global_brace('{')
                    data_structure_tracker.add_object_brace('{')

                results = indent_helper(indentation, tab_size, clean_lines, 
                                        data_structure_tracker, temp_line_num)

                for error in results:
                    self.add_error(**error)
            else:
                #TODO Figure out what it means to not have braces in the right place
                pass
        else:
            temp_line_num = self.current_line_num
            data_structure_tracker = DataStructureTracker()

            if check_if_struct_or_class(code):
                data_structure_tracker.add_object_brace("{")
                data_structure_tracker.in_class_or_struct = True

            data_structure_tracker.brace_stack.append('{')
            results = indent_helper(indentation, tab_size, clean_lines, 
                                    data_structure_tracker, temp_line_num)
            for error in results:
                self.add_error(**error)
    else:
        return
