from setuptools import setup

setup(
    name="183style",
    description="University of Michigan EECS 183 style grader.",
    install_requires=open("requirements.txt", "r").readlines(),
    packages=["eecs183style"],
    package_data={"eecs183style": ["rubric.ini"]},
    scripts=["bin/183style"]
)
