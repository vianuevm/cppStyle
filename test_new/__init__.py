from style_grader_functions import *
from StyleRubric import *
import os.path

TEST_SOURCE_PATH = os.path.abspath(os.path.dirname(__file__))

def load_code_segment(filename):
    def wrapper(func):
        def fn(self, *args, **kwargs):
            #Redirect stdout because it's annoying
            #tempout,temperr = sys.stdout, sys.stderr
            #sys.stdout = sys.stderr = open(os.devnull, 'w')
            self.rubric = StyleRubric()
            self.rubric.grade_student_file("{}/test_source/{}".format(
                TEST_SOURCE_PATH,
                filename
            ))
            #sys.stdout, sys.stderr = tempout, temperr
            return func(self, *args, **kwargs)
        return fn
    return wrapper

