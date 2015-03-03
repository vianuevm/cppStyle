#!/usr/bin/python
from test_new import load_code_segment
from style_grader_functions import *
from StyleRubric import *
import unittest

class RegressionTesting(unittest.TestCase):
    @load_code_segment('logical_AND_OR_spacing_bad.cpp')
    def test_bad_logical_spacing(self): self.assertTrue(self.rubric.error_types['OPERATOR_SPACING'] == 4)
    @load_code_segment('logical_AND_OR_spacing_good.cpp')
    def test_good_logical_spacing(self): self.assertTrue(self.rubric.error_types['OPERATOR_SPACING'] == 1)
    @load_code_segment('operator_spacing_bad.cpp')
    def test_bad_operator_spacing(self): self.assertTrue(self.rubric.error_types['OPERATOR_SPACING'] == 21)
    @load_code_segment('operator_spacing_good.cpp')
    def test_good_operator_spacing(self): self.assertTrue(self.rubric.error_types['OPERATOR_SPACING'] == 3)
