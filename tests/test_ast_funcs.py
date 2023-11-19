from textwrap import dedent

from superhelp import ast_funcs, gen_utils

from tests import get_actual_result

def test_get_el_list_lines_dets():
    """
    b'<Module>
        <body>
            <Import lineno="1" col_offset="0">
                <names><alias type="str" name="random"/></names>
            </Import>
            <Assign lineno="3" col_offset="0">
                <targets>
                    <Name lineno="3" col_offset="0" type="str" id="options">
                        <ctx><Store/></ctx>
                    </Name>
                </targets>
                <value>
                    <List lineno="3" col_offset="10">
                        <elts>
                            <Constant lineno="4" col_offset="4" type="str" value="apple"/>
                            <Constant lineno="5" col_offset="4" type="str" value="banana"/>
                            <Constant lineno="6" col_offset="4" type="str" value="cherry"/>
                        </elts>
                        <ctx><Load/></ctx>
                    </List>
                </value>
            </Assign>
            <Assign lineno="8" col_offset="0">
                <targets>
                    <Name lineno="8" col_offset="0" type="str" id="snack"><ctx><Store/></ctx></Name>
                </targets>
            <value><Call lineno="8" col_offset="8"><func><Attribute lineno="8" col_offset="8" type="str" attr="choice">
            <value><Name lineno="8" col_offset="8" type="str" id="random"><ctx><Load/>
            </ctx></Name></value>
            <ctx><Load/></ctx></Attribute></func><args><Name lineno="8" col_offset="22" type="str" id="options"><ctx><Load/></ctx></Name></args><keywords/></Call></value></Assign>
            <Expr lineno="9" col_offset="0">
            <value><Call lineno="9" col_offset="0"><func><Name lineno="9" col_offset="0" type="str" id="print"><ctx><Load/></ctx></Name></func>
            <args><Name lineno="9" col_offset="6" type="str" id="snack"><ctx><Load/></ctx></Name></args><keywords/></Call></value></Expr>
        </body>
        <type_ignores/>
    </Module>'
    """
    tests = [
        (dedent("""\
            import random

            options = [
                'apple',
                'banana',
                'cherry',
            ]
            snack = random.choice(options)
            print(snack)
            """), (3, 7, 5)),
        (dedent("""\
            import random


            options = [
                'apple',
                'banana',
                'cherry',
            ]
            snack = random.choice(options)
            print(snack)
            """), (4, 8, 5)),
        (dedent("""\
            import random

            options = [
                'apple',
                'banana',
                'cherry',
                'dates',
            ]
            snack = random.choice(options)
            print(snack)
            """), (3, 8, 6)),
        (dedent("""\
            import random

            options = ['apple',
                'banana',
                'cherry',
                'dates', ]
            snack = random.choice(options)
            print(snack)
            """), (3, 6, 4)),
        (dedent("""\
            import random

            options = ['apple',
                'banana', 'cherry', 'dates', ]
            snack = random.choice(options)
            print(snack)
            """), (3, 4, 2)),
    ]
    for snippet, expected_line_dets in tests:
        tree = gen_utils.get_tree(snippet, debug=True)
        xml = gen_utils.xml_from_tree(tree)
        first_list_el = xml.xpath('descendant-or-self::List')[0]
        actual_line_dets = ast_funcs.general.get_el_lines_dets(first_list_el)
        assert actual_line_dets == expected_line_dets

# test_get_el_list_lines_dets()

def test_num_str_from_parent_el():
    simple = "a = 10"
    neg = "a = -6"
    zero = "a = 0"
    non_num = "a = 'chicken'"
    simple2num_key = "a[1] = 100"
    simple2str_key = "a['chicken'] = 100"
    simple2obj_attr = "a.chicken = 100"
    neg2num_key = "a[1] = -100"
    neg2str_key = "a['chicken'] = -100"
    neg2obj_attr = "a.chicken = -100"
    xpath = 'descendant::Assign/value'
    tests = [
        (simple, '10'),
        (neg, '-6'),
        (zero, '0'),
        (non_num, None),
        (simple2num_key, '100'),
        (simple2str_key, '100'),
        (simple2obj_attr, '100'),
        (neg2num_key, '-100'),
        (neg2str_key, '-100'),
        (neg2obj_attr, '-100'),
    ]
    for snippet, expected_res in tests:
        actual_res = get_actual_result(
            snippet, xpath, ast_funcs.num_str_from_parent_el)
        assert actual_res == expected_res

# test_num_str_from_parent_el()
