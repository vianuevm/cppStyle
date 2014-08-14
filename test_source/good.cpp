/*
 * good.cpp
 *
 * First Last
 * uniqname@umich.edu
 *
 * A sample file for EECS 183 Style Grader.
 *
 * Demonstrates good style.
 */

#include <iostream>
using namespace std;

/**
 * Requires: Nothing.
 * Modifies: stdout.
 * Effects:  Greets the world.
 */
void greet(void);

int main(int argc, const char * argv[])
{
    // greet the user
    greet();
    cout << "bye." << endl;

    return 0;
}

void greet(void)
{
    cout << "o hai world!" << endl;
    cout << "o hai world!" << endl;
}
