Frequently asked questions
==========================


What's this and why should I care?
-----------------------------------------

**Raider** was developed with the goal to improve web
:ref:`authentication <definition_authentication>` testing. It feels
like everyone is writing their own custom tools which work only on
their systems, and this project aims to fill that gap and help test
more efficiently.


How does it work?
--------------------------

**Raider** uses a configuration directory containing a set of ``.hy``
files for each new project. Those files contain information describing
the authentication process. **Raider** evaluates them, and gives you
back a Python object to interact with the application.


How do I run this?
------------------

For now, only by writing a short Python script. However a CLI is
planned to be done soon.


Do I need to know Python and Hylang in order to use **Raider**?
---------------------------------------------------------------

Yes, **Raider** documentation already assumes you know the basic
concepts in both Python and Hylang. You don't have to know a lot. If
it's your first time with Python, just get yourself familiar with it,
and when you're ready move on to learning Hylang, which is basically
just Python code surrounded by Lisp parentheses.


Why Lisp?
---------

Because in Lisp code is data, and data is code. First iterations
through planning this project were done with a static configuration
file, experimenting with different formats. However, it turns out all
of those static formats had problems. They can't easily execute code,
they can't hold data structures, etc... Changing this to a Lisp file,
all those problems vanished away, and it gives the user the power to
add features easily without messing with the main code.



Why is Raider using Hylang?
---------------------------

Because the main code is written in Python. After deciding to choose
Lisp for the new configuration format, I obviously googled "python
lisp", and found this project. Looking through the documentation
I realized it turns out to be the perfect fit for my needs.


Does it work on Windows?
------------------------

Probably not. I don't have enough time to test it on other platforms.


What about macOS? BSD? etc?
---------------------------

I didn't test it, but should probably work as long as it's unix-like.

