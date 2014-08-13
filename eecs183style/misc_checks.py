def check_pointer_reference_consistency(self):
    if self.spacer.asts_left:
        if self.spacer.amps_right or self.spacer.amps_both:
            self.add_error(label='POINTER_REFERENCE_CONSISTENCY')
    elif self.spacer.asts_right:
        if self.spacer.amps_left or self.spacer.amps_both:
            self.add_error(label='POINTER_REFERENCE_CONSISTENCY')

