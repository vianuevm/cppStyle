def adjust_rme_in_header(self):
    # adjust missing RME error if RME is in a #included header file
    for filename in self.missing_rme.iterkeys():
        extension = filename.split('.')[-1]
        if extension == 'cpp':
            name = filename.split('.')[0]
            full_header_filename = name + '.h'
            # dealing with file paths
            short_header_filename = full_header_filename.split('/')[-1]

            # check if header is #included
            if short_header_filename in self.local_includes[filename]:
                for missing_rme in self.missing_rme[filename]:
                    # remove error if RME is present or missing (to avoid double-counting) in the header file
                    if missing_rme in self.all_rme.get(full_header_filename) or \
                        missing_rme in self.missing_rme.get(full_header_filename):
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
