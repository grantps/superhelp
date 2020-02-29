from pathlib import Path  #@UnresovedImport
import webbrowser

import conf

HTML_TAGS = {
    conf.H1: ('<h1>', '</h1>'),
    conf.P: ('<p>', '</p>'),
}

def get_html_strs(msg_dets):
    str_html_list = []
    for item in msg_dets:
        start_tag, end_tag = HTML_TAGS[item.type]
        str_html_list.append(f"{start_tag}{item.content}{end_tag}")
    return str_html_list

def show_explanations(explanations):
    all_html_strs = []
    explained_fpath = Path.cwd() / 'explained.html'
    with open(explained_fpath, 'w') as f:
        for explanation in explanations:
            for msg_type in conf.MSG_TYPES:
                try:
                    msg_dets = explanation[msg_type]
                except KeyError:
                    pass
                else:
                    msg_html_strs = get_html_strs(msg_dets)
                    all_html_strs.extend(msg_html_strs)
        f.write('\n'.join(all_html_strs))
    url = explained_fpath.as_uri()
    webbrowser.open_new_tab(url)
