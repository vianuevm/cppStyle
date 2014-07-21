import re
from pyparsing import Word, Literal, alphanums

def check_line_width(self, line):
    max_length = self.max_line_length
    current_length = len(line)
    if current_length > max_length:
        self.add_error(label="LINE_WIDTH", data={'length': current_length})

def check_missing_rme(self, lines):
    function = Word(alphanums + '_')
    function_syntax = function + Literal('(')
    parsed = function_syntax.searchString(lines[self.current_line_num]).asList()
    function_name = parsed[0][0]
    function_signature = lines[self.current_line_num].strip().replace(';','').strip()
    if function_name != 'main':
        requires = effects = modifies = False
        #Check if there's a complete RME in the last 10 lines
        for line_num in range(self.current_line_num - 10, self.current_line_num):
            code = lines[line_num].lower()
            if re.search('requires', code): requires = True
            if re.search('effects', code): effects = True
            if re.search('modifies', code): modifies = True
        # If it's not there, maybe they defined it in a header file.
        if not (requires and effects and modifies) and (function_signature not in self.all_rme[self.current_file]):
            # error only in this case
            # prevent double-counting
            if function_signature not in self.missing_rme[self.current_file]:
                self.add_error("MISSING_RME", data={'function': function_name, 'function_signature': function_signature})
                self.missing_rme[self.current_file].add(function_signature)

        elif function_signature not in self.all_rme[self.current_file]:
            self.all_rme[self.current_file].add(function_signature)

def check_min_comments(self, all_lines, clean_lines):
    num_lines = len(all_lines) + 1
    num_comments = 0
    for index, line in enumerate(all_lines):
        if line != clean_lines[index]:
            num_comments += 1
    if num_comments < num_lines * self.min_comments_ratio:
        self.add_error(label='MIN_COMMENTS', line=0, type="WARNING", data={'comments': num_comments, 'lines': num_lines})