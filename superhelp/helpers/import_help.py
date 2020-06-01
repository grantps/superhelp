from .. import conf
from ..gen_utils import layout_comment as layout
from ..helpers import all_blocks_help

MAIN_EXTERNAL_LIBS = conf.STD_LIBS + conf.POPULAR_LIBS

def internal_importing(block_dets):
    from_import_els = block_dets.element.xpath('descendant-or-self::ImportFrom')
    from_internal_els = [el for el in from_import_els
        if el.get('module') not in MAIN_EXTERNAL_LIBS]
    if from_internal_els:
        return True
    direct_import_els = block_dets.element.xpath('descendant-or-self::Import')
    for import_el in direct_import_els:
        direct_name_els = import_el.xpath('names/alias')
        direct_names = [el.get('name') for el in direct_name_els]
        non_main_external = set(direct_names) - set(MAIN_EXTERNAL_LIBS)
        if non_main_external:
            return True
    return False

@all_blocks_help()
def internal_imports(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for use of internal libraries. Explain the correct use of absolute
    imports and ways of combining those with code organisation into folders.

    Don't worry about false positives - there is no downside in providing the
    explanation when code has reached a certain level e.g. using libraries
    outside of the usual.

    <ImportFrom lineno="4" col_offset="0" type="int" module="os" level="0">
      <names>
        <alias type="str" name="getcwd"/>  
    <Import lineno="2" col_offset="0">
      <names>
        <alias type="str" name="requests"/>
    """
    if repeat:
        return None
    has_internal = False
    for block_dets in blocks_dets:
        block_has_internal = internal_importing(block_dets)
        if block_has_internal:
            has_internal = True
        break
    if not has_internal:
        return None

    title = layout("""\
    ### Successful Internal Importing
    """)
    brief_msg = layout("""\

        Importing internal modules when your code is in a folder structure is
        simple if you follow some basic rules:

        1) __Use absolute importing__ e.g. packagefolder.subfolder.modname

        2) If absolute importing is not working, don't do "crazy random stuff"
        from Stack Overflow - instead, __check `sys.path` is correct__. Look at
        the value for `sys.path` inside the module which is failing to import
        the internal module. If `sys.path` doesn't contain the path to the
        folder surrounding / outside / above the package folder, that is the
        cause of the problem and that is what you need to fix.
        """)
    main_msg = (
        layout("""\

        For example, imagine we have a package called `superhelp` with a module
        `conf.py` and subfolder `displayers`. Inside the subfolder is a module
        called `html_displayer`. The package is inside a folder called
        `/home/g/projects`.
        """)
        +
        layout("""\
        /home/g/projects       <------------- surrounding folder
            
                superhelp      <------------- package folder

                    conf.py       <---------- module

                    displayers    <---------- subfolder

                        html_displayer   <--- module
        """, is_code=True)
        +
        layout("""\

        Modules should refer to other internal modules using the full package
        path. So if a module wants to import `conf.py` it should import:

        `superhelp.conf` (package.module)

        If a module wants to import `html_displayer` it should import:

        `superhelp.displayers.html_displayer` (package.subfolder.module)

        In both cases it is crucial that `sys.path` contains `/home/g/projects`
        (surrounding folder)

        If working in an IDE, `sys.path` can probably be set to contain the
        surrounding folder.

        If using IDLE, start by opening IDLE from the surrounding folder.

        Only hack `sys.path` inside your code as a last resort.
        """)
    )
    extra_msg = layout("""\

    Some people like the elegance of the dot notation of relative importing but
    you need to know what you're doing if you use it. Relative importing only
    really makes sense if you're making code to be run as a library.

    Any modules in your library you want to run as scripts while developing
    (e.g. to get access to line-by-line debugging from your IDE) must use
    absolute importing for internal modules they reference AND sys.path must
    include the surrounding folder (i.e. just the usual rules explained
    earlier).

    Note – other modules you don’t want to run directly can continue to use
    relative importing – even if they are imported (absolutely) from modules you
    will be running directly as scripts.
    """)

    message = {
        conf.BRIEF: title + brief_msg,
        conf.MAIN: title + brief_msg + main_msg,
        conf.EXTRA: extra_msg,
    }
    return message
