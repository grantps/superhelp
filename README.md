# https://git.nzoss.org.nz/pyGrant/superhelp

version number: 0.9.4
author: Grant Paton-Simpson

## Overview

Superhelp is Help for Humans! The goal is to provide customised help for
simple code snippets. Superhelp is not intended to replace the built-in Python
help but to supplement it for basic Python code structures. Superhelp will
also be opinionated. Help can be provided in a variety of contexts including
the terminal and web browsers (perhaps as part of on-line tutorials).

## Quick Start

Click the button below to open a Binder Jupyter Notebook you can play around
in e.g. get advice on a line or snippet of Python

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fgit.nzoss.org.nz%2FpyGrant%2Fsuperhelp.git/master?filepath=notebooks%2FSuperhelpDemo.ipynb)

## Installation

Note - Python 3.6+ only. If you have an older version of Python use the Binder
Jupyter Notebook button instead (see higher up)

To install

1) Use pip e.g.

    $ pip3 install superhelp

or similar

    $ python3 -m pip install superhelp

2) Or clone the repo

    $ git clone https://git.nzoss.org.nz/pyGrant/superhelp.git
    $ python3 setup.py install

## Example Use Cases

* Charlotte is a Python beginner and wants to get advice on a five-line
function she wrote to display greetings to a list of people. She learns about
Python conventions for variable naming and better ways of combining strings.

* Avi wants to get advice on a named tuple. He learns how to add doc strings
to individual fields.

* Zach is considering submitting some code to Stack Overflow but wants to
improve it first (or possibly get ideas for a solution directly). He discovers
that a list comprehension might work. He also becomes aware of dictionary
comprehensions for the first time.

* Noor has written a simple Python decorator but is wanting to see if there is
anything which can be improved. She learns how to use functool.wrap from an
example provided.

* Al is an experienced Python developer but tends to forget things like doc
strings in his functions. He learns a standard approach and starts using it
more often.

# Example Usage

## Screenshot from HTML

![Example HTML output](https://git.nzoss.org.nz/pyGrant/superhelp/-/raw/master/example_html_output_1.png)

## Screenshot from Terminal

![Example Terminal output](https://git.nzoss.org.nz/pyGrant/superhelp/-/raw/master/example_terminal_output_1.png)

## Notebook

Add new cell at end with content like:

    %%shelp
    
    def sorted(my_list):
        sorted_list = my_list.sort()
        return sorted_list

and run it to get advice.

The notebook has more detailed instructions at the top.

## Local Installation

    $ shelp -h  ## get help on usage

    $ shelp --snippet "people = ['Tomas', 'Sal', 'Raj']" --displayer html --level Main
    $ shelp -s "people = ['Tomas', 'Sal', 'Raj']" -d html -l Main

    $ shelp --file-path my_snippet.py --displayer cli  --level Extra
    $ shelp -f snippet1.txt -d cli -l Brief

    $ shelp  ## to see advice on an example snippet displayed (level Extra)

    
## TODO Options

1) Extend advice further to encourage sound practice

2) Perhaps add style linting as an option

3) Extend beyond standard library into popular libraries like requests, bottle, flask etc.
