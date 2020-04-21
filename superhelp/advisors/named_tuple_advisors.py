from collections import namedtuple

from ..advisors import snippet_advisor
from .. import conf
from ..utils import layout_comment

NTDets = namedtuple('NamedTupleDetails', 'name, label, fields_str, fields_list')

def get_named_tuple_dets(named_tuple_el):
    """
    Get name, label, fields.
    """
    ancestor_elements = named_tuple_el.xpath('ancestor-or-self::*')
    assign_block_el = ancestor_elements[-5]  ##  Assign value Call func Name
    name = assign_block_el.xpath('targets/Name')[0].get('id')
    label_el, fields_el = assign_block_el.xpath('value/Call/args/Str')
    label = label_el.get('s')
    fields_str = fields_el.get('s')
    fields_list = [field.strip() for field in fields_str.split(',')]
    named_tuple_dets = NTDets(name, label, fields_str, fields_list)
    return named_tuple_dets

def get_named_tuples_dets(blocks_dets):
    all_named_tuples_dets = []
    for block_dets in blocks_dets:
        func_name_els = block_dets.element.xpath(
            'descendant-or-self::value/Call/func/Name')
        named_tuple_els = [func_name_el for func_name_el in func_name_els
            if func_name_el.get('id') == 'namedtuple']
        named_tuples_dets = [
            get_named_tuple_dets(named_tuple_el)
            for named_tuple_el in named_tuple_els]
        all_named_tuples_dets.extend(named_tuples_dets)
    return all_named_tuples_dets

@snippet_advisor()
def named_tuple_overview(blocks_dets):
    """
    Look for named tuples and explain how they can be enhanced.
    """
    named_tuples_dets = get_named_tuples_dets(blocks_dets)
    if not named_tuples_dets:
        return None
    example_dets = named_tuples_dets[0]
    first_field = example_dets.fields_list[0]
    brief_comment = (
            layout_comment("""\

                #### Named Tuple Enhancements

                Named tuples can be enhanced to make them even more useful -
                especially when debugging. The label can be expanded beyond the
                variable name; and the entire named tuple or individual fields
                can be given their own doc strings.

                For example:

                """)
            +
            layout_comment(f"""\
                {example_dets.name} = namedtuple("{example_dets.label}",
                    "{example_dets.fields_str}")
                {example_dets.name}.__doc__ += "\\n\\nExtra comments"
                {example_dets.name}.{first_field}.__doc__ = "Specific comment for {first_field}"
                ## etc
                """, is_code=True)
        )
    main_comment = (
        brief_comment
        +
        layout_comment("""\

            Default arguments are another nice option (added in Python 3.7). For
            example the following named tuple has a default IQ of 100:
            """)
        +
        layout_comment("""\

            People = namedtuple('PeopleDets', 'name, IQ', defaults=(100, ))
            """, is_code=True)
        +
        layout_comment("""\

            The official documentation has more details.
            """)
    )
    message = {
        conf.BRIEF: brief_comment,
        conf.MAIN: main_comment,
    }
    return message
    