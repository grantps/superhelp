from pathlib import Path  #@UnresovedImport
from textwrap import dedent, indent
import webbrowser

import conf

from markdown import markdown  ## https://coderbook.com/@marcus/how-to-render-markdown-syntax-as-html-using-python/

MSG_TYPE2CLASS = {
    msg_type: f"help help-{msg_type}" for msg_type in conf.MSG_TYPES}

HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
{head}
<body>
<img src='superhelp_logo.svg' float='left' width=70px>
<h1>SuperHELP - Help for Humans!</h1>
<p>Help is provided for each line of your snippet.
Toggle between different levels of detail.</p>
{radio_buttons}
{body_inner}
{visibility_script}
</body>
</html>"""

CODE_CSS = """\
/*From https://richleland.github.io/pygments-css/ */
.codehilite .hll { background-color: #ffffcc }
.codehilite  { background: #f8f8f8; }
.codehilite .c { color: #408080; font-style: italic } /* Comment */
.codehilite .err { border: 1px solid #FF0000 } /* Error */
.codehilite .k { color: #008000; font-weight: bold } /* Keyword */
.codehilite .o { color: #666666 } /* Operator */
.codehilite .ch { color: #408080; font-style: italic } /* Comment.Hashbang */
.codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
.codehilite .cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
.codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #A00000 } /* Generic.Deleted */
.codehilite .ge { font-style: italic } /* Generic.Emph */
.codehilite .gr { color: #FF0000 } /* Generic.Error */
.codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
.codehilite .gi { color: #00A000 } /* Generic.Inserted */
.codehilite .go { color: #888888 } /* Generic.Output */
.codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
.codehilite .gt { color: #0044DD } /* Generic.Traceback */
.codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
.codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
.codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
.codehilite .kp { color: #008000 } /* Keyword.Pseudo */
.codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
.codehilite .kt { color: #B00040 } /* Keyword.Type */
.codehilite .m { color: #666666 } /* Literal.Number */
.codehilite .s { color: #BA2121 } /* Literal.String */
.codehilite .na { color: #7D9029 } /* Name.Attribute */
.codehilite .nb { color: #008000 } /* Name.Builtin */
.codehilite .nc { color: #0000FF; font-weight: bold } /* Name.Class */
.codehilite .no { color: #880000 } /* Name.Constant */
.codehilite .nd { color: #AA22FF } /* Name.Decorator */
.codehilite .ni { color: #999999; font-weight: bold } /* Name.Entity */
.codehilite .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
.codehilite .nf { color: #0000FF } /* Name.Function */
.codehilite .nl { color: #A0A000 } /* Name.Label */
.codehilite .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
.codehilite .nt { color: #008000; font-weight: bold } /* Name.Tag */
.codehilite .nv { color: #19177C } /* Name.Variable */
.codehilite .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
.codehilite .w { color: #bbbbbb } /* Text.Whitespace */
.codehilite .mb { color: #666666 } /* Literal.Number.Bin */
.codehilite .mf { color: #666666 } /* Literal.Number.Float */
.codehilite .mh { color: #666666 } /* Literal.Number.Hex */
.codehilite .mi { color: #666666 } /* Literal.Number.Integer */
.codehilite .mo { color: #666666 } /* Literal.Number.Oct */
.codehilite .sa { color: #BA2121 } /* Literal.String.Affix */
.codehilite .sb { color: #BA2121 } /* Literal.String.Backtick */
.codehilite .sc { color: #BA2121 } /* Literal.String.Char */
.codehilite .dl { color: #BA2121 } /* Literal.String.Delimiter */
.codehilite .sd { color: #BA2121; font-style: italic } /* Literal.String.Doc */
.codehilite .s2 { color: #BA2121 } /* Literal.String.Double */
.codehilite .se { color: #BB6622; font-weight: bold } /* Literal.String.Escape */
.codehilite .sh { color: #BA2121 } /* Literal.String.Heredoc */
.codehilite .si { color: #BB6688; font-weight: bold } /* Literal.String.Interpol */
.codehilite .sx { color: #008000 } /* Literal.String.Other */
.codehilite .sr { color: #BB6688 } /* Literal.String.Regex */
.codehilite .s1 { color: #BA2121 } /* Literal.String.Single */
.codehilite .ss { color: #19177C } /* Literal.String.Symbol */
.codehilite .bp { color: #008000 } /* Name.Builtin.Pseudo */
.codehilite .fm { color: #0000FF } /* Name.Function.Magic */
.codehilite .vc { color: #19177C } /* Name.Variable.Class */
.codehilite .vg { color: #19177C } /* Name.Variable.Global */
.codehilite .vi { color: #19177C } /* Name.Variable.Instance */
.codehilite .vm { color: #19177C } /* Name.Variable.Magic */
.codehilite .il { color: #666666 } /* Literal.Number.Integer.Long */
"""

INTERNAL_CSS = """\
body {
  background-color: white;
  margin: 60px 80px 80px 80px;
}
h1, h2 {
  color: #3b3f74;
  font-weight: bold;
}
h1 {
  font-size: 16px;
}
h2 {
  font-size: 14px;
  margin-top: 24px;
}
h3 {
  font-size: 12px;
}
h4 {
  font-size: 11px;
}
.warning h4 {
  margin: 0;
}
p {
  font-size: 10px;
}
label {
  font-size: 12px;
}
.warning {
  border-radius: 3px;
  padding: 6px;
  margin: 0;
  border: 1px solid #d86231;
}
.help {
  display: none;
}
.help.help-visible {
  display: inherit;
}
%s
""" % CODE_CSS

HTML_HEAD = f"""\
<head>
<meta charset="utf-8">
<meta content="IE=edge" http-equiv="X-UA-Compatible">
<title>SuperHELP - Help for Humans!</title>
<style type="text/css">
{INTERNAL_CSS}
</style>
</head>"""

VISIBILITY_SCRIPT = """\
<script>
 function updateVerbosity() {
   var verbositySelectors = {
     '%(brief)s': '.help-%(brief)s',
     '%(main)s': '.help-%(main)s',
     '%(extra)s': '.help-%(main)s, .help-%(extra)s'
   }
   // Get selected verbosity.
   var verbosity = document.querySelector('input[name="verbosity"]:checked').value;
   // Hide all helps.
   document.querySelectorAll('.help').forEach(function(helpElement) {
     helpElement.classList.remove('help-visible');
   });
   // Show only selected helps.
   document.querySelectorAll(verbositySelectors[verbosity]).forEach(function(helpElement) {
     helpElement.classList.add('help-visible');
   });
 }

 // Update verbosity after page load.
 updateVerbosity();

 // Update verbosity whenever a radio is changed.
 var radios = document.querySelectorAll('input[name="verbosity"]');
 radios.forEach(function(radio) {
   radio.addEventListener('change', updateVerbosity);
 });
</script>
""" % {'brief': conf.BRIEF, 'main': conf.MAIN, 'extra': conf.EXTRA}

def get_html_strs(msg, msg_type,*, warning=False):
    div_class = MSG_TYPE2CLASS[msg_type]
    warning_class = ' warning' if warning else ''
    str_html_list = [f"<div class='{div_class}{warning_class}'>", ]
    msg_str = markdown(dedent(msg))
    str_html_list.append(msg_str)
    str_html_list.append("</div>")
    return str_html_list

def _get_all_html_strs(explanations_dets):
    """
    Display all message types - eventually will show brief and, if the user
    clicks to expand, main instead with the option of expanding to show Extra.
    """
    all_html_strs = []
    explanations_dets.sort(key=lambda nt: (nt.line_no))
    prev_line_no = None
    for explanation_dets in explanations_dets:
        ## display code for line number (once ;-))
        line_no = explanation_dets.line_no
        if line_no != prev_line_no:
            all_html_strs.append(f'<h2>Line {line_no:,}</h2>')
            code_content = indent(
                f"::python\n{explanation_dets.content}",
                ' '*4)
            content = markdown(code_content, extensions=['codehilite'])
            all_html_strs.append(content)
            prev_line_no = line_no
        ## process messages
        for msg_type in conf.MSG_TYPES:
            try:
                msg = explanation_dets.explanation[msg_type]
            except KeyError:
                if msg_type != conf.EXTRA:
                    raise Exception(f"Missing required message type {msg_type}")
            else:
                msg_html_strs = get_html_strs(
                    msg, msg_type, warning=explanation_dets.warning)
                all_html_strs.extend(msg_html_strs)
    return all_html_strs

def _get_radio_buttons(*, msg_level=conf.BRIEF):
    radio_buttons_dets = []
    for msg_type in conf.MSG_TYPES:
        checked = ' checked' if msg_type == msg_level else ''
        radio_button_dets = f"""\
            <input type="radio"
             id="radio-verbosity-{msg_type}"
             name="verbosity"
             value="{msg_type}"{checked}>
            <label for="radio-verbosity-{msg_type}">{msg_type}</label>
            """
        radio_buttons_dets.append(radio_button_dets)
    radio_buttons = '\n'.join(radio_buttons_dets)
    return radio_buttons

def show(explanations_dets, *, msg_level=conf.BRIEF):
    """
    Show by lines and then by list_rules within line.
    """
    radio_buttons = _get_radio_buttons(msg_level=msg_level)
    all_html_strs = _get_all_html_strs(explanations_dets)
    body_inner = '\n'.join(all_html_strs)
    html2write = HTML_WRAPPER.format(
        head=HTML_HEAD, radio_buttons=radio_buttons, body_inner=body_inner,
        visibility_script=VISIBILITY_SCRIPT)
    explained_fpath = Path.cwd() / 'explained.html'
    with open(explained_fpath, 'w') as f:
        f.write(html2write)
    url = explained_fpath.as_uri()
    webbrowser.open_new_tab(url)
