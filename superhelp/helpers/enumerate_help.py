from ..helpers import all_blocks_help
from .. import ast_funcs, conf
from ..gen_utils import layout_comment as layout

def get_var_initialised(el):
    """
    e.g. var i if
    i = 0 or i = -1 or i = 1

    ## 3.8+ example where a positive number
    <Assign lineno="1" col_offset="0">
      <targets>
        <Name lineno="1" col_offset="0" type="str" id="counter">
          <ctx>
            <Store/>
          </ctx>
        </Name>
      </targets>
      <value>
        <Constant lineno="1" col_offset="10" type="int" value="0"/>
      </value>
    </Assign>
    """
    assign_els = el.xpath('descendant-or-self::Assign')
    if not assign_els:
        return None
    has_var_init = False
    for assign_el in assign_els:
        value_els = assign_el.xpath('value')
        if len(value_els) != 1:
            continue
        num = ast_funcs.num_str_from_val(value_els[0])
        if num not in ['0', '-1', '1']:
            continue
        name_els = assign_el.xpath('targets/Name')
        if not name_els:
            continue
        name = name_els[0].get('id')
        has_var_init = True
        break
    var_initialised = name if has_var_init else None
    return var_initialised

def get_incrementing_var(el):
    """
    Get name of incrementing variable.

    e.g. i if i += 1 or i = i + 1
    """
    var_incremented = ast_funcs._get_var_plus_equalled(el)
    if not var_incremented:
        var_incremented = ast_funcs._get_var_equal_plussed(el)
    return var_incremented

def get_incrementing_vars(for_el):
    """
    Look at children for incrementation. Do any has signs of incrementation?
    Collect vars that do.
    """
    children = for_el.getchildren()
    incrementing_vars = []
    for child in children:
        incrementing_var = get_incrementing_var(child)
        if incrementing_var:
            incrementing_vars.append(incrementing_var)
    return incrementing_vars

def get_init_vars(for_el):
    """
    Get variable names that have been initialised in a pattern common when
    preparing for manual incrementation.

    Do previous siblings have common patterns of variable incrementer
    initialisation? Collect any vars that do.
    """
    init_vars = []
    for prev_sibling_el in for_el.itersiblings(preceding=True):
        var_initialised = get_var_initialised(prev_sibling_el)
        if var_initialised:
            init_vars.append(var_initialised)
    return init_vars

def get_manual_incrementing_var(for_el):
    """
    Get first manual incrementing var.

    Look at previous siblings for common patterns of variable incrementer
    initialisation. Then look at children for incrementation. If we find both,
    we have found likely manual incrementation.
    """
    init_vars = get_init_vars(for_el)
    if not init_vars:
        return None
    incrementing_vars = get_incrementing_vars(for_el)
    if not incrementing_vars:
        return None
    manual_incrementing_vars = sorted(
        set(init_vars).intersection(set(incrementing_vars)))
    if manual_incrementing_vars:
        return manual_incrementing_vars[0]
    else:
        return None

@all_blocks_help()
def manual_incrementing(blocks_dets, *, repeat=False, **_kwargs):
    """
    Look for manual handling of incrementing inside for loops.
    """
    for_els = []
    for block_dets in blocks_dets:
        for_els.extend(block_dets.element.xpath('descendant-or-self::For'))
    if not for_els:
        return None
    incrementing_var = None
    for for_el in for_els:
        incrementing_var = get_manual_incrementing_var(for_el)
        if incrementing_var:
            break
    if not incrementing_var:
        return None

    summary = layout(f"""\
    ### Possible option of using `enumerate()`

    It looks like your code is manually incrementing `{incrementing_var}`. In
    Python you can use the `enumerate` function to handle this for you.
    """)
    if not repeat:
        demo = (
            layout("""\
            Here is an example of the manual approach:
            """)
            +
            layout("""\
            n = 1
            for image in images:
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
                n += 1
            """, is_code=True)
            +
            layout("""\
            Here is how we can use `enumerate()` instead:
            """)
            +
            layout("""\
            for n, image in enumerate(images, 1):
                if n % 10 == 0:
                    print(f"Just processed image {{n}}")
                process_image(image)
            """, is_code=True)
            +
            layout("""\

            Often you want counting from 0 in which case you don't need to
            specify the start value (0 is the default):
            """)
            +
            layout("""\
            for i, image in enumerate(images):
                ...
            """, is_code=True)
            +
            layout("""\

            You can give the enumerated value any name that makes sense but
            reserve `i` for incrementing starting at 0 and prefer `n` when
            starting at 1.
            """)
        )
    else:
        demo = ''

    message = {
        conf.BRIEF: summary,
        conf.MAIN: summary + demo,
    }
    return message
