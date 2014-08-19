from distutils.core import setup

setup(
    name="183style",
    description="University of Michigan EECS 183 style grader.",
    packages=["eecs183style"],
    package_data={"eecs183style": ["rubric.ini"]},
    scripts=["bin/183style"]
)
