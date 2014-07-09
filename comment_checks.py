import re

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
    # If it's not there, maybe they defined it in a header file.
    # Finish this later
    if not (requires and effects and modifies):
        self.add_error(label="MISSING_RME")
