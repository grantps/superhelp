from ..helpers import all_blocks_help
from .. import ast_funcs, conf
from ..gen_utils import layout_comment as layout

def imported_re(block_el):
    ## straight import
    import_els = block_el.xpath('descendant-or-self::Import/names/alias')
    import_names = [el.get('name') for el in import_els]
    if 're' in import_names:
        return True
    import_from_module_els = block_el.xpath('descendant-or-self::ImportFrom')
    from_import_names = [el.get('module') for el in import_from_module_els]
    if 're' in from_import_names:
        return True
    return False

def _imported_verbose_constant_attr(block_el):
    attr_els = block_el.xpath('descendant-or-self::value/Attribute')
    verbose_constant = False
    for attr_el in attr_els:
        if attr_el.get('attr') == conf.VERBOSE_FLAG:
            verbose_constant = True
            break
    return verbose_constant

def _from_imported_verbose_constant(block_el):
    import_from_els = block_el.xpath('descendant-or-self::ImportFrom')
    verbose_constant = False
    for import_from_el in import_from_els:
        name_alias_els = import_from_el.xpath('descendant-or-self::names/alias')
        for name_alias_el in name_alias_els:
            if name_alias_el.get('name') == conf.VERBOSE_FLAG:
                verbose_constant = True
                break
    return verbose_constant
    
def used_verbose_constant(block_el):
    if _imported_verbose_constant_attr(block_el):
        return True
    if _from_imported_verbose_constant(block_el):
        return True
    return False

def used_inline_verbose(block_el):
    used_inline_verbose = False
    ## Treating presence of '(?x)' as sign of in-line verbose mode indicator.
    ## To be honest, if it actually is there for another reason the worst that
    ## happens is we don't let them know about verbose option when we could have
    str_els = ast_funcs.str_els_from_block(block_el)
    for str_el in str_els:
        str_val = ast_funcs.str_from_el(str_el)
        if str_val and str_val.startswith(conf.INLINE_RE_VERBOSE_FLAG):
            used_inline_verbose = True
            break
    return used_inline_verbose

def used_verbose(block_el):
    if used_verbose_constant(block_el):
        return True
    if used_inline_verbose(block_el):
        return True
    return False

def used_compile(block_el):
    pass

@all_blocks_help()
def verbose_option(blocks_dets, *, repeat=False, **_kwargs):
    """
    Check for use of regex without verbose mode and introduce the idea.
    """
    has_imported_re = False
    has_used_verbose = False
    for block_dets in blocks_dets:
        block_el = block_dets.element
        if not has_imported_re:
            if imported_re(block_el):
                has_imported_re = True
        if not has_used_verbose:
            if used_verbose(block_el):
                has_used_verbose = True
        if has_imported_re and has_used_verbose:
            break
    needs_verbose = has_imported_re and not has_used_verbose
    if not needs_verbose:
        return None

    title = layout("""\
    ### Option of using verbose mode with regex
    """)
    if not repeat:
        tm = '\N{TRADE MARK SIGN}'
        brief_explain = layout(f"""\

        Regular expressions are infamous for being hard to understand, hard to
        debug, and hard to maintain / extend. It is sometimes said that when you
        have a problem, and you solve it with regex, now you have two problems
        ;-). So anything you can do to make your regex more readable is a very
        Good Thing{tm}. Which is where verbose mode is often helpful.
        """)
        longer_explain = (
                layout("""\

                Verbose mode lets you split your regex into smaller, more
                manageable parts, and you can comment your intentions for each
                part. The following example is hard enough to understand _with_
                comments - imagine trying to make sense of it without! Or make
                modifications without breaking everything. Good luck with that!
                """)
                +
                layout('''\
                pattern = r"""
                    (?P<before_id>
                    var\sdiv_icon_                    ## var div_icon
                    \w+                               ## lots of characters (don't care which until ...)
                    \s=\sL.divIcon\(\{[\s\S]*?\<div)  ##  = L.divIcon({ anything till <div (non-greedy)
                    (?P<after_id>[\s\S]*? ;)          ## anything until first semi-colon (we're non-greedy
                                                      ## so we can pick up multiple instances of pattern)
                    """
                ''', is_code=True)
                +
                layout("""\

                Note - because whitespace is ignored it must be explicitly
                handled in your pattern. In some cases the overhead of doing
                this will outweigh the benefits of using verbose mode.
                """)
                +
                layout("""\
                You can either use the verbose flag e.g.
                """)
                +
                layout("""\
                re.match(r'car', 'cardboard', flags=re.VERBOSE)
                """, is_code=True)
                +
                layout("""\
                or the in-line version of the flag e.g.
                """)
                +
                layout("""\
                re.match(r'(?x)car', 'cardboard')
                """, is_code=True)
            )
        extra = layout("""\

        The standard documentation at
        <https://docs.python.org/3/howto/regex.html> is really good. Having said
        that, regex is never trivial so don't worry if you find it challenging.

        Pronunciation: reggex or rejex? Regex with a hard 'g' probably makes
        most sense because regular also has a hard 'g' but there is no consensus
        on pronunciation.
        """)
    else:
        brief_explain = ''
        longer_explain = ''
        extra = ''

    message = {
        conf.BRIEF: title + brief_explain,
        conf.MAIN: title + longer_explain,
        conf.EXTRA: extra,
    }
    return message
