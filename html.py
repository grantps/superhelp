from pathlib import Path  #@UnresovedImport
import webbrowser

import conf

HTML_TAGS = {
    conf.H1: ('<h3>', '</h3>'),  ## reserving h1 for title and h2 for line number, everything else demoted accordingly
    conf.H1: ('<h4>', '</h4>'),
    conf.P: ('<p>', '</p>'),
}

MSG_TYPE2CLASS = {
    conf.BRIEF: 'help help-brief',
    conf.MAIN: 'help help-main',
    conf.EXTRA: 'help help-extra',
}

HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
{head}
<h1>SuperHELP on your Python code</h1>
<body>
<input type="radio" id="radio-verbosity-brief" name="verbosity" value="brief" checked>
<label for="radio-verbosity-brief">Brief</label>
<input type="radio" id="radio-verbosity-main" name="verbosity" value="main">
<label for="radio-verbosity-main">Main</label>
<input type="radio" id="radio-verbosity-extra" name="verbosity" value="extra">
<label for="radio-verbosity-extra">Extra</label>
{body_inner}
{visibility_script}
</body>
</html>"""

HTML_HEAD = """\
<head>
<meta charset="utf-8">
<meta content="IE=edge" http-equiv="X-UA-Compatible">
<title>SuperHELP</title>
<style type="text/css">
body {
  background-color: white;
  margin: 80px;
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
}
h3 {
  font-size: 12px;
}
h4 {
  font-size: 11px;
}
p {
  font-size: 10px;
}
.code {
  font-family: courier mono;
}
.warning {
  border-radius: 6px;
  padding: 6px;
  border: 1px solid #d86231;
  width: 400px;
}
.help {
  display: none;
}
.help.help-visible {
  display: inherit;
}
</style>
</head>"""

VISIBILITY_SCRIPT = """\
<script>
 function updateVerbosity() {
   var verbositySelectors = {
     'brief': '.help-brief',
     'main': '.help-main',
     'extra': '.help-main, .help-extra'
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
"""

def get_html_strs(msg_dets, msg_type,*, warning=False):
    div_class = MSG_TYPE2CLASS[msg_type]
    warning_class = ' warning' if warning else ''
    str_html_list = [f"<div class='{div_class}{warning_class}'>", ]
    for item in msg_dets:
        start_tag, end_tag = HTML_TAGS[item.semantic_role]
        str_html_list.append(f"{start_tag}{item.msg}{end_tag}")
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
            all_html_strs.append(f'<h1>Line {line_no:,}</h1>')
            content = (explanation_dets.content
                .replace('\n', '</br>')
                .replace('    ', '&nbsp;'*4))
            all_html_strs.append(f"<p class='code'>{content}</p>")
            prev_line_no = line_no
        ## process messages
        for msg_type in conf.MSG_TYPES:
            try:
                msg_dets = explanation_dets.explanation[msg_type]
            except KeyError:
                pass
            else:
                msg_html_strs = get_html_strs(
                    msg_dets, msg_type, warning=explanation_dets.warning)
                all_html_strs.extend(msg_html_strs)
    return all_html_strs

def show(explanations_dets):
    """
    Show by lines and then by rules within line.
    """
    explained_fpath = Path.cwd() / 'explained.html'
    with open(explained_fpath, 'w') as f:
        all_html_strs = _get_all_html_strs(explanations_dets)
        html_body = '\n'.join(all_html_strs)
        html2write = HTML_WRAPPER.format(
            head=HTML_HEAD, body_inner=html_body,
            visibility_script=VISIBILITY_SCRIPT)
        f.write(html2write)
    url = explained_fpath.as_uri()
    webbrowser.open_new_tab(url)
