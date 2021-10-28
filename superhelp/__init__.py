"""
From a code point of view we have a pipeline.

The initial input is a snippet of code, or a script file path,
or a folder (possibly nested) of script files.

This is converted into an iterable of code items (often only one item)
e.g. from code pasted into a text box, from a folder of scripts etc.

This is turned into an iterable of code item details which in turn ...

are handled by a formatter which in turn produces an iterable of formatted
text.

If the help content is being directly display then it is passed to a displayer
e.g. an HTML displayer.
It either displays it all at once or bit by bit depending on the display type.
E.g. CLI output is incremental and HTML is all-at-once.

The reason for having a pipeline is twofold:

* so we can delegate display to another program e.g. to a Jupyter notebook
  or perhaps an online superhelp web interface.
* so output can be delivered in a lazy fashion - there is no point generating
  all the formatted help if the user doesn't ask for the next installment of
  help in a multi-script context.

Note - ignoring warning caused by import of this because it allows the following
simple end-user syntax:

import superhelp
superhelp.this()
"""

import warnings
warnings.filterwarnings('ignore', '.*prior to execution of.*')

from superhelp.helper import this
