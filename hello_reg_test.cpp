//Test num_of_commands-----------------------
s++; e++;
x = 5 + 3 / 7; 1; 34;
w = 
3 + 4; d++;
x = 5;
myFn();
code on
two lines;

//Test valid_return---------------------------
bool myFn(void) {
    return 4;
bool myFn(void) {return 0;}
bool myFn(void) {
    return false;
}
bool myFn(void) {return true;}


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
void greet(void)
{
    cout << "o hai world!" << endl;
    cout << "o hai world!" << endl;
}

int main(int argc, const char * argv[])
{
    // greet the user
    greet();
    cout << "bye." << endl;

    return 0;
}
//if_else_good-----------------------------
int main() {
    if(x == 5) {
        cout << "yes!" << endl;
    }
    else {
        cout << "yes!" << endl;
    }
    if (x == 5)
    {
        cout << "yes!" << endl;
    }
    else if (x == 5)
    {
        cout << "elif" << endl;
    }
    else
    {
        cout << "else" << endl;
    }
    if (x == 5) { cout << "yes!" << endl; }
    else { cout << "else" << endl; }
}
//if_else_bad-----------------------------
int main() {
    if (x == 5) cout << "no" << endl;
    else if (x == 3) 
        cout << "no";
    else {
        cout << "maybe?"
    }
    else cout << "no!";
}
//equals_true----------------------------
if (x == true) {
if (blah == true)
if (function.call(arguments, secondarg) == true)
if (check->across_pointer.call(5, args) == true)
if (true == check->across_pointer.call(5, args))
//-----------------------------------
