import re
from pyparsing import Word, Literal, alphanums

def check_line_width(self, line):
    max_length = 80
    current_length = len(line)
    if current_length > max_length:
        self.add_error(label="LINE_WIDTH", data={'length': current_length})

def check_missing_rme(self, lines):
    function = Word(alphanums + '_')
    function_syntax = function + Literal('(')
    parsed = function_syntax.searchString(lines[self.current_line_num]).asList()
    function_name = parsed[0][0]
    if function_name != 'main':
        requires = effects = modifies = False
        #Check if there's a complete RME in the last 10 lines
        for line_num in range(self.current_line_num - 10, self.current_line_num):
            code = lines[line_num].lower()
            if re.search('requires', code): requires = True
            if re.search('effects', code): effects = True
            if re.search('modifies', code): modifies = True
        # If it's not there, maybe they defined it in a header file. #TODO: check only #included files
        if (function_name not in self.all_rme) and not (requires and effects and modifies):
            self.add_error("MISSING_RME", data={'function': function_name})
        elif (requires and effects and modifies):
            self.all_rme.add(function_name)
