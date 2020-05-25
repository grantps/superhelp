from textwrap import dedent, indent
import webbrowser

from .. import conf, gen_utils

from markdown import markdown  ## https://coderbook.com/@marcus/how-to-render-markdown-syntax-as-html-using-python/ @UnresolvedImport

DETAIL_LEVEL2CLASS = {
    detail_level: f"help help-{detail_level}"
    for detail_level in conf.DETAIL_LEVELS}

BROWSER_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
{head}
<body>
{logo_svg}
<h1>SuperHELP - Help for Humans!</h1>
{intro}
<p>{missing_advice_message}</p>
<p>Toggle between different levels of detail.</p>
{radio_buttons}
{body_inner}
{visibility_script}
</body>
</html>"""

NOTEBOOK_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
{head}
<body>
<h1>Look here for some help on the snippet in the cell above</h1>
{intro}
<p>{missing_advice_message}</p>
<p>Toggle between different levels of detail.</p>
{radio_buttons}
{body_inner}
{visibility_script}
</body>
</html>"""

CODE_CSS = """\
/*From https://richleland.github.io/pygments-css/ */
.codehilite .hll { background-color: #ffffcc }
.codehilite {
  background: #f8f8f8;
  padding: 6px 4px 4px 12px;
}
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

PART = 'part'
IS_CODE = 'is_code'

def _get_radio_buttons(*, detail_level=conf.BRIEF):
    radio_buttons_dets = []
    for message_type in conf.DETAIL_LEVELS:
        checked = ' checked' if message_type == detail_level else ''
        radio_button_dets = f"""\
            <input type="radio"
             id="radio-verbosity-{message_type}"
             name="verbosity"
             value="{message_type}"{checked}>
            <label for="radio-verbosity-{message_type}">{message_type}</label>
            """
        radio_buttons_dets.append(radio_button_dets)
    radio_buttons = '\n'.join(radio_buttons_dets)
    return radio_buttons

def get_separate_code_message_parts(message):
    """
    Need to handle code portions differently so need to separate it out.

    :return: list of message part details
     [{'part': 'asdf', 'is_code': False}, ...]
    :rtype: list
    """
    message_parts = []
    open_code_block = False
    lines = message.split('\n')
    for i, line in enumerate(lines):
        first_line = i == 0
        line_in_code_block = line.startswith(' ' * 4)
        if line_in_code_block:
            if open_code_block:
                open_code_part = message_parts[-1]
                open_code_part[PART] += f"\n{line}"  ## add to already-open code part
            else:
                message_parts.append({PART: line, IS_CODE: True})  ## start new code part
            open_code_block = True
        else:  ## line not in a code block
            if first_line or open_code_block:
                message_parts.append({PART: line, IS_CODE: False})
            else:
                open_non_code_part = message_parts[-1]
                open_non_code_part[PART] += f"\n{line}"
            open_code_block = False
    return message_parts

def get_html_strs(message, message_type, *, warning=False):  # @UnusedVariable
    if not message:
        return []
    message_type_class = DETAIL_LEVEL2CLASS[message_type]
    str_html_list = [f"<div class='{message_type_class}'>", ]
    message_parts = get_separate_code_message_parts(message)
    for message_part in message_parts:
        if message_part[IS_CODE]:
            message_part_str = markdown(
                message_part[PART], extensions=['codehilite'])
        else:
            message_part_str = markdown(
                dedent(message_part[PART]))
        str_html_list.append(message_part_str)
    str_html_list.append("</div>")
    return str_html_list

def get_message_html_strs(message_dets):
    """
    Process message.
    """
    message_html_strs = []
    if message_dets.warning:
        message_html_strs.append("<div class='warning'>")
    for detail_level in conf.DETAIL_LEVELS:
        try:
            message = message_dets.message[detail_level]
        except KeyError:
            if detail_level != conf.EXTRA:
                raise Exception(
                    f"Missing required message level {detail_level}")
        except TypeError:
            raise TypeError(
                f"Missing message in message_dets {message_dets}")
        else:
            try:
                message = (
                    message
                    .replace(conf.PYTHON_CODE_START, conf.MD_PYTHON_CODE_START)
                    .replace(f"\n    {conf.PYTHON_CODE_END}", '')
                )
            except Exception:
                pass
            detail_level_html_strs = get_html_strs(
                message, detail_level, warning=message_dets.warning)
            message_html_strs.extend(detail_level_html_strs)
    if message_dets.warning:
        message_html_strs.append("</div>")
    return message_html_strs

def repeat_overall_snippet(snippet, file_path):
    html_strs = []
    code_desc = gen_utils.get_code_desc(file_path)
    html_strs.append(f"<h2>{code_desc}</h2>")
    line_numbered_snippet = gen_utils.get_line_numbered_snippet(snippet)
    overall_code_str = indent(
        f"{conf.MD_PYTHON_CODE_START}\n{line_numbered_snippet}",
        ' '*4)
    overall_code_str_highlighted = markdown(
        overall_code_str, extensions=['codehilite'])
    html_strs.append(overall_code_str_highlighted)
    return html_strs

def _need_snippet_displayed(overall_messages_dets, block_messages_dets, *,
        in_notebook=False, multi_block=False):
    """
    Don't need to see the code snippet displayed when it is already visible
    right next to it:
    * because in notebook (it is already in the cell straight above)
    * because there is only one block in snippet and there is a block message
      for it (which will display the block i.e. the entire snippet) UNLESS there
      is an overall message separating them
    Otherwise we need it displayed.
    """
    if in_notebook:
        return False
    mono_block_snippet = not multi_block
    if mono_block_snippet and block_messages_dets and not overall_messages_dets:
        return False
    return True

def _get_all_html_strs(snippet, file_path,
        overall_messages_dets, block_messages_dets, *,
        warnings_only=False, in_notebook=False, multi_block=False):
    """
    Display all message types - eventually will show brief and, if the user
    clicks to expand, main instead with the option of expanding to show Extra.

    Suppress overall snippet display if in notebook - it is right above already
    and repeating it is confusing and obscures the feedback.
    """
    all_html_strs = []

    ## any feedback on user options chosen
    if not in_notebook:
        if warnings_only:
            options_msg = f"<p>{conf.WARNINGS_ONLY_MSG}.</p>"
        else:
            options_msg = f"<p>{conf.ALL_HELP_SHOWING_MSG}.</p>"
        all_html_strs.append(options_msg)
        all_html_strs.append("<div id='star'>"
            "Help by spreading the word about SuperHELP on social media.<br>"
            f"Twitter: {conf.TWITTER_HANDLE}. Thanks!</div>")
    ## overall snippet display
    display_snippet = _need_snippet_displayed(
        overall_messages_dets, block_messages_dets,
        in_notebook=in_notebook, multi_block=multi_block)
    if display_snippet:
        overall_snippet_html_strs = repeat_overall_snippet(snippet, file_path)
        all_html_strs.extend(overall_snippet_html_strs)

    ## overall messages
    overall_messages_dets.sort(key=lambda nt: nt.warning)
    for message_dets in overall_messages_dets:
        message_html_strs = get_message_html_strs(message_dets)
        all_html_strs.extend(message_html_strs)

    ## block messages
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no, nt.warning))  ## by code block then within blocks warnings last
    prev_line_no = None
    for message_dets in block_messages_dets:
        ## display code for line number (once ;-)) Each line might have one or more messages but it will always have the one code_str starting on that line
        line_no = message_dets.first_line_no
        new_block = (line_no != prev_line_no)
        if new_block:
            block_has_warning_header = False
            all_html_strs.append(
                f'<h2>Code block starting line {line_no:,}</h2>')
            block_code_str = indent(
                f"{conf.MD_PYTHON_CODE_START}\n{message_dets.code_str}",
                ' '*4)
            block_code_str_highlighted = markdown(
                block_code_str, extensions=['codehilite'])
            all_html_strs.append(block_code_str_highlighted)
            prev_line_no = line_no
        if message_dets.warning and not block_has_warning_header:
            all_html_strs.append("<h3>Questions / Warnings</h3>")
            all_html_strs.append("<p>There may be some issues with this code "
                "block you want to address.</p>")
            block_has_warning_header = True
        message_html_strs = get_message_html_strs(message_dets)
        all_html_strs.extend(message_html_strs)
    return all_html_strs

def _get_head(*, in_notebook=False):
    internal_css = conf.INTERNAL_CSS % {
        'code_css': CODE_CSS,
        'margin_css': '' if in_notebook else 'margin: 40px 70px 20px 70px;',
        'max_width_css': '' if in_notebook else 'max-width: 700px;'
    }
    head = conf.HTML_HEAD % {
        'internal_css': internal_css}
    return head

def display(snippet, file_path, messages_dets, *,
        detail_level=conf.BRIEF,
        in_notebook=False, warnings_only=False,
        multi_block=False, multi_script=False):
    """
    Show for overall snippet and then by code blocks as appropriate.

    :param bool in_notebook: if True, return HTML as string; else open browser
     and display
    """
    raw_intro = gen_utils.get_intro(file_path, multi_block=multi_block)
    intro = f"<p>{raw_intro}</p>" if raw_intro else ''
    radio_buttons = _get_radio_buttons(detail_level=detail_level)
    overall_messages_dets, block_messages_dets = messages_dets
    all_html_strs = _get_all_html_strs(snippet, file_path,
        overall_messages_dets, block_messages_dets, warnings_only=warnings_only,
        in_notebook=in_notebook, multi_block=multi_block)
    body_inner = '\n'.join(all_html_strs)
    head = _get_head(in_notebook=in_notebook)
    if in_notebook:
        html2write = NOTEBOOK_HTML_WRAPPER.format(
            head=head,
            radio_buttons=radio_buttons,
            intro=intro,
            missing_advice_message=conf.MISSING_ADVICE_MESSAGE,
            body_inner=body_inner,
            visibility_script=VISIBILITY_SCRIPT)
        deferred_display = html2write
        return deferred_display
    else:
        html2write = BROWSER_HTML_WRAPPER.format(
            head=head, logo_svg=conf.LOGO_SVG,
            radio_buttons=radio_buttons,
            intro=intro,
            missing_advice_message=conf.MISSING_ADVICE_MESSAGE,
            body_inner=body_inner,
            visibility_script=VISIBILITY_SCRIPT)
        if file_path:
            raw_file_name = gen_utils.clean_path_name(file_path)
            file_name = f'{raw_file_name}.html'
        else:
            file_name = 'superhelp_output.html'
        superhelp_tmpdir = gen_utils.get_superhelp_tmpdir(
            folder=conf.SUPERHELP_PROJECT_OUTPUT)
        with gen_utils.make_open_tmp_file(
                file_name, superhelp_tmpdir=superhelp_tmpdir,
                mode='w') as tmp_dets:
            _superhelp_tmpdir, tmp_fh, fpath = tmp_dets
            tmp_fh.write(html2write)
        if multi_script:
            pass  ## display is deferred
        else:
            url = fpath.as_uri()
            webbrowser.open_new_tab(url)
