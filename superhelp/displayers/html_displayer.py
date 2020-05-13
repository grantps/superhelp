from textwrap import dedent, indent
import webbrowser

from .. import conf
from ..utils import get_line_numbered_snippet, make_open_tmp_file

from markdown import markdown  ## https://coderbook.com/@marcus/how-to-render-markdown-syntax-as-html-using-python/ @UnresolvedImport

DETAIL_LEVEL2CLASS = {
    detail_level: f"help help-{detail_level}"
    for detail_level in conf.DETAIL_LEVELS}

LOGO_SVG = """\
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="100.11089mm"
   height="79.607109mm"
   viewBox="0 0 100.11089 79.607109"
   version="1.1"
   id="svg8"
   inkscape:version="0.92.4 (5da689c313, 2019-01-14)"
   sodipodi:docname="superhelp_logo.svg"
   inkscape:export-filename="/home/g/projects/superhelp/superhelp/store/superhelp_logo.png"
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
     inkscape:cx="76.737316"
     inkscape:cy="121.00951"
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
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-53.753912,-82.960833)">
    <g
       transform="translate(-57.326112,-175.59945)"
       id="g9171">
      <path
         inkscape:connector-curvature="0"
         id="path4991-3-6"
         transform="matrix(0.26458333,0,0,0.26458333,-8.3176424,-7.9183424)"
         d="m 591.57422,1011.6934 a 83.098512,82.305791 18.437406 0 0 -53.05664,20.1914 83.098512,82.305791 18.437406 0 0 -26.49805,78.3183 83.098512,82.305791 18.437406 0 0 54.18164,61.5059 l -0.0371,0.1113 123.08203,41.0332 -2.51171,7.6485 -123.47461,-41.1661 v 0 l -77.85938,-25.957 a 82.244946,81.781039 18.437412 0 0 -1.26562,38.1523 82.244946,81.781039 18.437412 0 0 54.88671,61.3047 l 0.004,-0.01 123.56055,41.1914 -0.008,0.021 a 82.216504,82.216504 0 0 0 0.46094,0.1309 l 0.33594,0.1113 0.006,-0.016 a 82.216504,82.216504 0 0 0 80.125,-16.7149 82.216504,82.216504 0 0 0 25.77344,-78.4648 82.216504,82.216504 0 0 0 -53.91602,-60.75 v 0 l -0.16992,-0.057 a 82.216504,82.216504 0 0 0 -1.30274,-0.4551 l -0.006,0.02 -121.01758,-40.3458 2.64843,-7.83 119.71485,39.9121 -0.002,0.01 78.07226,26.0293 c 3.44134,-12.4392 14.87561,-39.3166 12.27344,-51.9727 -5.95174,-28.611 -37.64693,-38.2382 -65.52734,-47.4199 -0.10692,-0.035 -0.21742,-0.072 -0.32422,-0.1074 l -121.63282,-40.5508 -0.0117,0.033 a 83.098512,82.305791 18.437406 0 0 -26.5039,-3.9062 z"
         style="fill:#0072aa;fill-opacity:1;stroke:none;stroke-width:32.70064163;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 273.07885,208.13282 a 3.2002347,3.2002347 0 0 1 3.20327,-3.19481 3.2002347,3.2002347 0 0 1 3.1972,3.20089 3.2002347,3.2002347 0 0 1 -3.1985,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="208.13824"
         sodipodi:cx="276.27908"
         sodipodi:type="arc"
         id="path5097-9-2"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 227.2124,219.8216 a 3.2002347,3.2002347 0 0 1 3.20327,-3.19481 3.2002347,3.2002347 0 0 1 3.19719,3.20089 3.2002347,3.2002347 0 0 1 -3.19849,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="219.82703"
         sodipodi:cx="230.41263"
         sodipodi:type="arc"
         id="path5097-0-7-8"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
      <path
         transform="rotate(18.437412)"
         sodipodi:open="true"
         d="m 258.29068,242.97 a 3.2002347,3.2002347 0 0 1 3.20327,-3.1948 3.2002347,3.2002347 0 0 1 3.19719,3.20089 3.2002347,3.2002347 0 0 1 -3.1985,3.19958 3.2002347,3.2002347 0 0 1 -3.20197,-3.19611"
         sodipodi:end="3.1403035"
         sodipodi:start="3.1432891"
         sodipodi:ry="3.2002347"
         sodipodi:rx="3.2002347"
         sodipodi:cy="242.97543"
         sodipodi:cx="261.49091"
         sodipodi:type="arc"
         id="path5097-0-9-7-8"
         style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:6.38603258;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />
    </g>
  </g>
</svg>
"""

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

INTERNAL_CSS = """\
body {
  background-color: white;
  %(margin_css)s
  %(max_width_css)s
}
h1, h2 {
  color: #0072aa;
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
blockquote {
  font-style: italic;
  color: #666666;
}
blockquote p {
  font-size: 13px;
}
svg {
  height: 50px;
  width: 60px;
}
.warning {
  border-radius: 2px;
  padding: 12px 6px 6px 12px;
  margin: 10px 0 0 0;
  border: 2px solid #0072aa;
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

def repeat_overall_snippet(snippet):
    html_strs = []
    html_strs.append("<h2>Overall Snippet</h2>")
    line_numbered_snippet = get_line_numbered_snippet(snippet)
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

def _get_all_html_strs(snippet, overall_messages_dets, block_messages_dets, *,
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
    ## overall snippet display
    display_snippet = _need_snippet_displayed(
        overall_messages_dets, block_messages_dets,
        in_notebook=in_notebook, multi_block=multi_block)
    if display_snippet:
        overall_snippet_html_strs = repeat_overall_snippet(snippet)
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
    internal_css = INTERNAL_CSS % {
        'code_css': CODE_CSS,
        'margin_css': '' if in_notebook else 'margin: 40px 70px 20px 70px;',
        'max_width_css': '' if in_notebook else 'max-width: 700px;'
    }
    head = HTML_HEAD % {
        'internal_css': internal_css}
    return head

def display(snippet, messages_dets, *,
        detail_level=conf.BRIEF,
        in_notebook=False, warnings_only=False, multi_block=False):
    """
    Show for overall snippet and then by code blocks as appropriate.

    :param bool in_notebook: if True, return HTML as string; else open browser
     and display
    """
    intro = f"<p>{conf.INTRO}</p>"
    radio_buttons = _get_radio_buttons(detail_level=detail_level)
    overall_messages_dets, block_messages_dets = messages_dets
    all_html_strs = _get_all_html_strs(snippet,
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
        return html2write
    else:
        html2write = BROWSER_HTML_WRAPPER.format(
            head=head, logo_svg=LOGO_SVG,
            radio_buttons=radio_buttons,
            intro=intro,
            missing_advice_message=conf.MISSING_ADVICE_MESSAGE,
            body_inner=body_inner,
            visibility_script=VISIBILITY_SCRIPT)
        tmp_fh, fpath = make_open_tmp_file('superhelp_output.html', mode='w')
        tmp_fh.write(html2write)
        tmp_fh.close()
        url = fpath.as_uri()
        webbrowser.open_new_tab(url)
