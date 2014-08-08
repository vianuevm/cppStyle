#!/usr/bin/python
from style_grader_functions import *
from StyleRubric import *
import unittest
import sys, os

def load_code_segment(filename):
    def wrapper(func):
        def fn(self, *args, **kwargs):
            #Redirect stdout because it's annoying
            #tempout,temperr = sys.stdout, sys.stderr
            #sys.stdout = sys.stderr = open(os.devnull, 'w')
            self.rubric = StyleRubric()
            self.rubric.grade_student_file('test_source/'+filename)
            #sys.stdout, sys.stderr = tempout, temperr  
            return func(self, *args, **kwargs)
        return fn
    return wrapper

class RegressionTesting(unittest.TestCase):

    def setUp(self):
        #Nothing to do here for now
        pass

    def tearDown(self):
        #For debugging FAILs
        #jprint "-- RESULTS ------------------"
        #for x,y in self.rubric.error_types.items():
        #    print x,y
        #print "-----------------------------\n\n"
        pass


    @load_code_segment('good.cpp')
    def test_good_file(self): self.assertTrue(not len(self.rubric.error_types))
    @load_code_segment('num_of_commands.cpp')
    def test_statements_per_line(self): self.assertEqual(self.rubric.error_types['STATEMENTS_PER_LINE'], 3)
    @load_code_segment('test_valid_return.cpp')
    def test_int_for_bool(self): self.assertEqual(self.rubric.error_types['INT_FOR_BOOL'], 2)
    #@load_code_segment('if_else_good.cpp')
    #def test_good_if_else(self): self.assertRaises(KeyError, self.rubric.error_types.get, 'IF_ELSE_ERROR')
    #@load_code_segment('if_else_bad.cpp')
    #def test_bad_if_else(self): self.assertEqual(3, self.rubric.error_types['IF_ELSE_ERROR'])
    @load_code_segment('equals_true.cpp')
    def test_equals_true(self): self.assertEqual(5, self.rubric.error_types['EQUALS_TRUE']) 

if __name__ == '__main__':
    print "\n"
    suite = unittest.TestLoader().loadTestsFromTestCase(RegressionTesting)
    unittest.TextTestRunner(verbosity=2).run(suite)
