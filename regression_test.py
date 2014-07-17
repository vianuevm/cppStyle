#!/usr/bin/python
from style_grader_functions import *
from StyleRubric import *
import unittest
import sys, os

'''
The basics of Python's unittest module:
Each test should begin with test_
Name each test after the function being tested
3 general ways to check results:
    self.assertEqual()
    self.assertTrue()
    self.assertRaises()
'''

'''
Decorator to load the appropriate lines so there's no error collision.
Use it as @load_code_segment(start_line, end_line) to load code lines in range [start_line, end_line)
'''
def load_code_segment(start, end):
    def wrapper(func):
        def fn(self, *args, **kwargs):
            #Redirect stdout because it's annoying
            tempout,temperr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = open(os.devnull, 'w')
            testfile = open('testing_file.cpp', 'w+')
            source = open('hello_reg_test.cpp', 'rU').readlines()
            for i in range(start-1, end-1):
                testfile.write(source[i])
            testfile.close()
            self.rubric = StyleRubric()
            self.rubric.grade_student_file('testing_file.cpp')
            sys.stdout, sys.stderr = tempout, temperr  
            return func(self, *args, **kwargs)
        return fn
    return wrapper

class RegressionTesting(unittest.TestCase):

    def setUp(self):
        #Nothing to do here for now
        pass

    def tearDown(self):
        #For debugging FAILs
        print "-- RESULTS ------------------"
        for x,y in self.rubric.error_types.items():
            print x,y
        print "-----------------------------\n\n"

    @load_code_segment(21,56)
    def test_good_file(self): self.assertTrue(not len(self.rubric.error_tracker[self.rubric.current_file]))
    @load_code_segment(1,10)
    def test_statements_per_line(self): self.assertEqual(self.rubric.error_types['STATEMENTS_PER_LINE'], 3)
    @load_code_segment(11,20)
    def test_int_for_bool(self): self.assertEqual(self.rubric.error_types['INT_FOR_BOOL'], 2)
    @load_code_segment(57,79)
    def test_good_if_else(self): self.assertRaises(KeyError, self.rubric.error_types.get, 'IF_ELSE_ERROR')
    @load_code_segment(80,89)
    def test_bad_if_else(self): self.assertEqual(3, self.rubric.error_types['IF_ELSE_ERROR'])
    @load_code_segment(90,95)
    def test_equals_true(self): self.assertEqual(5, self.rubric.error_types['EQUALS_TRUE']) 

if __name__ == '__main__':
    print "\n"
    suite = unittest.TestLoader().loadTestsFromTestCase(RegressionTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
