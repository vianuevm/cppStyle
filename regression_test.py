#!/usr/bin/python
from style_grader_functions import *
from StyleRubric import *
import unittest
import sys, os

'''
The basics of Python's unittest module:
Each test should begin with test_
Name each test after the function being tested
3 ways to check results:
    self.assertEqual()
    self.assertTrue()
    self.assertRaises()
Note that test_valid_return() breaks!
''' 

'''
Decorator to load the appropriate lines so there's no error collision.
Use it as @load_code_segment(start_line, end_line) to load code lines in range [start_line, end_line)
'''
def load_code_segment(start, end):
    def wrapper(func):
        def fn(self, *args, **kwargs):
            testfile = open('testing_file.cpp', 'w+')
            source = open('hello_reg_test.cpp', 'rU').readlines()
            for i in range(start-1, end-1):
                testfile.write(source[i])
            testfile.close()
            return func(self, *args, **kwargs)
        return fn
    return wrapper

class RegressionTesting(unittest.TestCase):

    def setUp(self):
        # Redirect stdout/err since it's annoying
        #tempout,temperr = sys.stdout, sys.stderr
        #sys.stdout = sys.stderr = open(os.devnull, 'w')
        print
        self.rubric = StyleRubric()
        self.rubric.grade_student_file('testing_file.cpp')
        for error in self.rubric.error_tracker:
            print error
        #sys.stdout, sys.stderr = tempout, temperr  

    @load_code_segment(21,53)
    def test_good_file(self): self.assertTrue(not len(self.rubric.error_tracker))    
    @load_code_segment(1,10)
    def test_num_of_commands(self): self.assertEqual(self.rubric.error_types['COMMAND_ERROR'], 3)
    @load_code_segment(11,20)
    def test_valid_return(self): self.assertEqual(self.rubric.error_types['BOOL_VALUE'], 2)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(RegressionTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
