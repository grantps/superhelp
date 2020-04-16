from pathlib import Path  #@UnresovedImport
from textwrap import dedent, indent
import webbrowser

from .. import conf

from markdown import markdown  ## https://coderbook.com/@marcus/how-to-render-markdown-syntax-as-html-using-python/ @UnresolvedImport

MESSAGE_LEVEL2CLASS = {
    message_level: f"help help-{message_level}"
    for message_level in conf.MESSAGE_LEVELS}

LOGO_SVG = """\
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="93.345726mm"
   height="65.921318mm"
   viewBox="0 0 93.345726 65.921318"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.4 (5da689c313, 2019-01-14)"
   sodipodi:docname="superhelp_logo.svg"
   inkscape:export-filename="/home/g/projects/superhelp/superhelp_logo.png"
   inkscape:export-xdpi="96"
   inkscape:export-ydpi="96">
  <defs
     id="defs2">
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4972"
       is_visible="true"
       pattern="m 60.80692,207.585 -0.62276,-0.0405 -0.15389,-0.6048 0.527651,-0.33326 0.479996,0.39885 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4944"
       is_visible="true"
       pattern="m 58.866112,205.1261 h 0.701582 v 0.66817 h -0.701582 z"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4907"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4889"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4861"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4820"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4721"
       is_visible="true"
       pattern="m 61.427734,769.66211 v 9.31641 h 7.748047 v -9.31641 z m 8.271485,0.0156 v 9.31446 h 7.748047 v -9.31446 z"
       copytype="repeated"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0.1"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect4694"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
    <inkscape:path-effect
       effect="skeletal"
       id="path-effect935"
       is_visible="true"
       pattern="M 0,0 H 1"
       copytype="single_stretched"
       prop_scale="1"
       scale_y_rel="false"
       spacing="0"
       normal_offset="0"
       tang_offset="0"
       prop_units="false"
       vertical_pattern="false"
       fuse_tolerance="0" />
  </defs>
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="1"
     inkscape:pageshadow="2"
     inkscape:zoom="1.979899"
     inkscape:cx="8.2743457"
     inkscape:cy="95.321425"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     inkscape:window-width="1869"
     inkscape:window-height="1056"
     inkscape:window-x="1971"
     inkscape:window-y="24"
     inkscape:window-maximized="1"
     fit-margin-top="0"
     fit-margin-left="0"
     fit-margin-right="0"
     fit-margin-bottom="0"
     inkscape:pagecheckerboard="false" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-55.880255,-89.849988)">
    <path
       style="fill:#3b3f74;fill-opacity:1;stroke:none;stroke-width:33.15284348;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       d="M 281.68359 0.00390625 C 277.92668 -0.0091550074 274.18542 0.01817 270.50586 0.03125 L 83.767578 0.03125 L 82.986328 0.03125 L 82.986328 0.04296875 A 82.216504 82.216504 0 0 0 11.845703 40.632812 A 82.216504 82.216504 0 0 0 11.480469 123.2207 A 82.216504 82.216504 0 0 0 81.882812 164.40234 L 81.882812 164.68555 L 268.19727 164.68555 L 268.2168 169.17773 L 82.296875 169.17773 L 0 169.17773 A 82.216501 84.506075 0 0 0 10.863281 206.99219 A 82.216501 84.506075 0 0 0 76.419922 248.88281 L 76.419922 249.14062 L 81.845703 249.14062 A 82.216501 84.506075 0 0 0 82.296875 249.15039 L 82.296875 249.14062 L 268.57031 249.14062 L 268.57031 249.15039 A 82.216504 82.216504 0 0 0 268.7793 249.14062 L 269.40234 249.14062 L 269.40234 249.11133 A 82.216504 82.216504 0 0 0 340.12891 207.91406 A 82.216504 82.216504 0 0 0 339.76367 125.32617 A 82.216504 82.216504 0 0 0 269.40234 84.746094 L 269.40234 84.722656 L 83.392578 84.722656 L 83.414062 79.994141 L 270.50586 79.994141 L 270.50586 80.003906 L 352.80273 80.003906 C 352.1333 66.694753 354.48107 36.631983 348.00977 25.083984 C 335.10234 2.1735036 307.98199 0.095335052 281.68359 0.00390625 z "
       transform="matrix(0.26458333,0,0,0.26458333,55.880255,89.849988)"
       id="path4991-7-1" />
    <path
       style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="path5097"
       sodipodi:type="arc"
       sodipodi:cx="140.07877"
       sodipodi:cy="98.10202"
       sodipodi:rx="3.2002347"
       sodipodi:ry="3.2002347"
       sodipodi:start="3.1432891"
       sodipodi:end="3.1403035"
       d="m 136.87854,98.096591 a 3.2002347,3.2002347 0 0 1 3.20327,-3.194804 3.2002347,3.2002347 0 0 1 3.19719,3.200885 3.2002347,3.2002347 0 0 1 -3.1985,3.199578 3.2002347,3.2002347 0 0 1 -3.20197,-3.196104"
       sodipodi:open="true" />
    <path
       style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="path5097-0"
       sodipodi:type="arc"
       sodipodi:cx="78.337524"
       sodipodi:cy="111.3783"
       sodipodi:rx="3.2002347"
       sodipodi:ry="3.2002347"
       sodipodi:start="3.1432891"
       sodipodi:end="3.1403035"
       d="m 75.137294,111.37287 a 3.2002347,3.2002347 0 0 1 3.203271,-3.1948 3.2002347,3.2002347 0 0 1 3.197194,3.20089 3.2002347,3.2002347 0 0 1 -3.198498,3.19958 3.2002347,3.2002347 0 0 1 -3.201969,-3.19611"
       sodipodi:open="true" />
    <path
       style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
       id="path5097-0-9"
       sodipodi:type="arc"
       sodipodi:cx="124.23225"
       sodipodi:cy="133.99762"
       sodipodi:rx="3.2002347"
       sodipodi:ry="3.2002347"
       sodipodi:start="3.1432891"
       sodipodi:end="3.1403035"
       d="m 121.03202,133.99219 a 3.2002347,3.2002347 0 0 1 3.20327,-3.1948 3.2002347,3.2002347 0 0 1 3.19719,3.20088 3.2002347,3.2002347 0 0 1 -3.1985,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.1961"
       sodipodi:open="true" />
  </g>
</svg>
"""

HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
{head}
<body>
{logo_svg}
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
  %(margin_css)s
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
h5 {
  font-size: 9px;
  font-style: italic;
}
p {
  font-size: 10px;
}
li {
  font-size: 10px;
}
label {
  font-size: 12px;
}
svg {
  height: 50px;
  width: 70px;
}
.warning {
  border-radius: 3px;
  padding: 6px;
  margin: 10px 0 0 0;
  border: 1px solid #d86231;
}
.help {
  display: none;
}
.help.help-visible {
  display: inherit;
}
%(code_css)s
"""

HTML_HEAD = f"""\
<head>
<meta charset="utf-8">
<meta content="IE=edge" http-equiv="X-UA-Compatible">
<title>SuperHELP - Help for Humans!</title>
<style type="text/css">
%(internal_css)s
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

PART = 'part'
IS_CODE = 'is_code'

def _get_radio_buttons(*, message_level=conf.BRIEF):
    radio_buttons_dets = []
    for message_type in conf.MESSAGE_LEVELS:
        checked = ' checked' if message_type == message_level else ''
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

def get_html_strs(message, message_type, *, warning=False):
    if not message:
        return []
    div_class = MESSAGE_LEVEL2CLASS[message_type]
    warning_class = ' warning' if warning else ''
    str_html_list = [f"<div class='{div_class}{warning_class}'>", ]
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
    for message_level in conf.MESSAGE_LEVELS:
        try:
            message = message_dets.message[message_level]
        except KeyError:
            if message_level != conf.EXTRA:
                raise Exception(
                    f"Missing required message level {message_level}")
        except TypeError:
            raise TypeError(
                f"Missing message in message_dets {message_dets}")
        else:
            message = (
                message
                .replace(conf.PYTHON_CODE_START, conf.MD_PYTHON_CODE_START)
                .replace(f"\n    {conf.PYTHON_CODE_END}", '')
            )
            message_level_html_strs = get_html_strs(
                message, message_level, warning=message_dets.warning)
            message_html_strs.extend(message_level_html_strs)
    return message_html_strs

def _get_all_html_strs(snippet, overall_messages_dets, block_messages_dets):
    """
    Display all message types - eventually will show brief and, if the user
    clicks to expand, main instead with the option of expanding to show Extra.
    """
    all_html_strs = []
    ## overall messages
    all_html_strs.append("<h2>Overall Snippet</h2>")
    overall_code_str = indent(
        f"{conf.MD_PYTHON_CODE_START}\n{snippet}",
        ' '*4)
    overall_code_str_highlighted = markdown(
        overall_code_str, extensions=['codehilite'])
    all_html_strs.append(overall_code_str_highlighted)
    for message_dets in overall_messages_dets:
        message_html_strs = get_message_html_strs(message_dets)
        all_html_strs.extend(message_html_strs)
    ## block messages
    block_messages_dets.sort(key=lambda nt: (nt.first_line_no))
    prev_line_no = None
    for message_dets in block_messages_dets:
        ## display code for line number (once ;-)) Each line might have one or more messages but it will always have the one code_str starting on that line
        line_no = message_dets.first_line_no
        if line_no != prev_line_no:
            all_html_strs.append(
                f'<h2>Code block starting line {line_no:,}</h2>')
            block_code_str = indent(
                f"{conf.MD_PYTHON_CODE_START}\n{message_dets.code_str}",
                ' '*4)
            block_code_str_highlighted = markdown(
                block_code_str, extensions=['codehilite'])
            all_html_strs.append(block_code_str_highlighted)
            prev_line_no = line_no
        message_html_strs = get_message_html_strs(message_dets)
        all_html_strs.extend(message_html_strs)
    return all_html_strs

def _get_head(*, in_notebook=False):
    internal_css = INTERNAL_CSS % {
        'code_css': CODE_CSS,
        'margin_css': '' if in_notebook else 'margin: 60px 80px 80px 80px;',
    }
    head = HTML_HEAD % {
        'internal_css': internal_css}
    return head

def display(snippet, messages_dets, *,
        message_level=conf.BRIEF, in_notebook=False):
    """
    Show for overall snippet and then by code blocks as appropriate.

    :param bool in_notebook: if True, return HTML as string; else open browser
     and display
    """
    radio_buttons = _get_radio_buttons(message_level=message_level)
    overall_messages_dets, block_messages_dets = messages_dets
    all_html_strs = _get_all_html_strs(snippet,
        overall_messages_dets, block_messages_dets)
    body_inner = '\n'.join(all_html_strs)
    head = _get_head(in_notebook=in_notebook)
    html2write = HTML_WRAPPER.format(
        head=head, logo_svg=LOGO_SVG,
        radio_buttons=radio_buttons, body_inner=body_inner,
        visibility_script=VISIBILITY_SCRIPT)
    if in_notebook:
        return html2write
    else:
        explained_fpath = Path.cwd() / 'explained.html'
        with open(explained_fpath, 'w') as f:
            f.write(html2write)
        url = explained_fpath.as_uri()
        webbrowser.open_new_tab(url)
