from .. import conf
from ..gen_utils import layout_comment as layout
from ..helpers import all_blocks_help

def _method_from_mod(block_dets, modname, methodname):
    """
    E.g.
    from os import getcwd
    from os.path import join
    from os.path import join as joinpath

    <ImportFrom lineno="4" col_offset="0" type="int" module="os" level="0">
      <names>
        <alias type="str" name="getcwd"/>    
    """
    importfrom_els = block_dets.element.xpath('descendant-or-self::ImportFrom')
    mod_els = [el for el in importfrom_els if el.get('module') == modname]
    if not mod_els:
        return False
    has_mod_method = False
    for mod_el in mod_els:
        names_els = mod_el.xpath('names/alias')
        methodname_els = [
            el for el in names_els if el.get('name') == methodname]
        if methodname_els:
            has_mod_method = True
            break
    return has_mod_method

def has_getcwd_from(block_dets):
    """
    from os import getcwd

    <ImportFrom lineno="4" col_offset="0" type="int" module="os" level="0">
      <names>
        <alias type="str" name="getcwd"/>
    """
    return _method_from_mod(block_dets, modname='os', methodname='getcwd')

def has_join_from(block_dets):
    """
    from os.path import join
    <ImportFrom lineno="2" col_offset="0" type="int" module="os.path" level="0">
      <names>
        <alias type="str" name="join"/>
    """
    return _method_from_mod(block_dets, modname='os.path', methodname='join')

def has_os_getcwd(block_dets):
    """
    os.getcwd()

    <func>
      <Attribute lineno="3" col_offset="0" type="str" attr="getcwd">
        <value>
          <Name lineno="3" col_offset="0" type="str" id="os">
    """
    func_attr_els = block_dets.element.xpath(
        'descendant-or-self::func/Attribute')
    getcwd_els = [el for el in func_attr_els if el.get('attr') == 'getcwd']
    if not getcwd_els:
        return False
    os_getcwd = False
    for getcwd_el in getcwd_els:
        val_name_els = getcwd_el.xpath('value/Name')
        os_els = [el for el in val_name_els if el.get('id') == 'os']
        if os_els:
            os_getcwd = True
            break
    return os_getcwd

def has_os_path(block_dets):
    """
    import os.path
    <Import lineno="2" col_offset="0">
      <names>
        <alias type="str" name="os.path"/>
    """
    import_els = block_dets.element.xpath(
        'descendant-or-self::Import/names/alias')
    if not import_els:
        return False
    has_os_path = False
    for import_el in import_els:
        os_path_els = import_el.xpath('names/alias')
        alias_os_path_els = [
            el for el in os_path_els if el.get('name') == 'os.path']
        if alias_os_path_els:
            has_os_path = True
            break
    return has_os_path

def has_os_path_join(block_dets):
    """
    path = os.path.join('a', 'b')
    os.path.join('a/', 'b')
    <value>
      <Call lineno="2" col_offset="7">
        <func>
          <Attribute lineno="2" col_offset="7" type="str" attr="join">
            <value>
              <Attribute lineno="2" col_offset="7" type="str" attr="path">
                <value>
                  <Name lineno="2" col_offset="7" type="str" id="os">
    """
    os_path_join_els = block_dets.element.xpath(
        'descendant-or-self::'
        'value/Call/func/Attribute/value/Attribute/value/Name')
    if len(os_path_join_els) != 1:
        return False
    join_els = block_dets.element.xpath(
        'descendant-or-self::value/Call/func/Attribute')
    if len(join_els) != 1:
        return False
    join_el =join_els[0]
    if not join_el.get('attr') == 'join':
        return False
    path_els = block_dets.element.xpath(
        'descendant-or-self::'
        'value/Call/func/Attribute/value/Attribute')
    if len(path_els) != 1:
        return False
    path_el = path_els[0]
    if not path_el.get('attr') == 'path':
        return False
    name_els = block_dets.element.xpath(
        'descendant-or-self::'
        'value/Call/func/Attribute/value/Attribute/value/Name')
    if len(name_els) != 1:
        return False
    name_el = name_els[0]
    if not name_el.get('id') == 'os':
        return False
    return True

@all_blocks_help()
def using_os(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for use of os.path.join, os.getcwd, etc and give general advice on when
    / how to use pathlib.

    os.getcwd()
    from os import getcwd
    import os.path
    path = os.path.join('a', 'b')
    from os.path import join
    from os.path import join as joinpath
    """
    give_pathlib_advice = False
    check_fns = [has_getcwd_from, has_join_from, has_os_getcwd, has_os_path,
        has_os_path_join]
    for block_dets in blocks_dets:
        if any(fn(block_dets) for fn in check_fns):  ## surprisingly although `any` does short-circuit, if you pass in list of called fns it has already run them all befor thus stuffig short-circuiting
            give_pathlib_advice = True
            break
    if not give_pathlib_advice:
        return None

    title = layout("""\
    ### Consider using `pathlib`
    """)
    if not repeat:
        brief_msg = layout("""\

        The `pathlib` library often provides a superior way of working with
        paths than `os` and `os.path`. It was introduced in Python 3.4.
        """)
        main_msg = (
            layout("""\

            The `pathlib` library often provides a superior way of working with
            paths than `os` and `os.path`. Instead of manipulating strings,
            `pathlib` has semantic methods and operators. Consider the following
            alternatives:
            """)
            +
            layout("""\
            #### `os` and `os.path`
            """)
            +
            layout("""\
            fpath = os.path.join(os.getcwd(), 'superhelp', 'conf.py')
            # '/home/g/Documents/python/python_scripts/superhelp/conf.py'

            parent = os.path.split(fpath)[0]
            # '/home/g/Documents/python/python_scripts/superhelp'

            fname = fpath.split('/')[-1]
            # 'conf.py'
            """, is_code=True)
            +
            layout("""\
            #### `pathlib`
            """)
            +
            layout("""\
            fpath = Path.cwd() / 'superhelp' / 'conf.py'
            # PosixPath('/home/g/Documents/python/python_scripts/superhelp/conf.py')

            parent = fpath.parent
            # PosixPath('/home/g/Documents/python/python_scripts/superhelp')

            fname = fpath.name
            # 'conf.py'
            """, is_code=True)
            +
            layout("""\

            The `pathlib` library was introduced in Python 3.4. Increasingly,
            functions expecting a path argument as a string will accept
            `pathlib` `Path`s as well. If a `Path` isn't accepted (yet) wrapping
            the path in `str()` creates the required string.
            """)
        )
        extra_msg =layout("""\
        Further advocacy can be found at:

        * <https://treyhunner.com/2019/01/no-really-pathlib-is-great/>

        * <https://treyhunner.com/2018/12/why-you-should-be-using-pathlib/>
        """)
    else:
        brief_msg = ''
        main_msg = ''
        extra_msg = ''

    message = {
        conf.BRIEF: title + brief_msg,
        conf.MAIN: title + main_msg,
        conf.EXTRA: extra_msg,
    }
    return message
