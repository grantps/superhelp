"""
Numbers are stored differently when they're negative.

## a positive number
<Assign lineno="1" col_offset="0">
  ...
  <value>
    <Constant lineno="1" col_offset="4" type="int" value="123"/>
  </value>
</Assign>

## a negative number
<Assign lineno="1" col_offset="0">
  ...
  <value>
    <UnaryOp lineno="1" col_offset="4">
      <op>
        <USub/>
      </op>
      <operand>
        <Constant lineno="1" col_offset="5" type="int" value="123"/>
      </operand>
    </UnaryOp>
  </value>
</Assign>

Python 3.8+ uses Constant; 3.6-3.7 used Num.
"""

def assigned_num_els_from_block(block_el):
    val_els = block_el.xpath('descendant-or-self::Assign/value')
    num_els = []
    for val_el in val_els:
        num_str = num_str_from_parent_el(parent_el=val_el)
        if num_str:
            neg_constant_els = val_el.xpath(
                'descendant-or-self::UnaryOp/operand/Constant')
            if neg_constant_els:
                neg_constant_el = neg_constant_els[0]
                num_els.append(neg_constant_el)
                continue
            else:
                pos_constant_els = val_el.xpath('descendant-or-self::Constant')
                pos_constant_el = pos_constant_els[0]
                num_els.append(pos_constant_el)
    return num_els

def _num_str_from_const_el(el):
    val = el.get('value')
    if el.get('type') in ('int', 'float'):
        num = val
    else:
        num = None
    return num

def _num_str_from_unaryop_el(el):
    sub_els = el.xpath('op/USub')
    if len(sub_els) != 1:
        return None
    negative_num_els = el.xpath('operand/Constant')
    if len(negative_num_els) != 1:
        return None
    negative_num_el = negative_num_els[0]
    pos_num = _num_str_from_const_el(negative_num_el)
    if pos_num is None:
        num = None
    else:
        num = f'-{pos_num}'
    return num

def num_str_from_el(el):
    if el.tag == 'Constant':
        num = _num_str_from_const_el(el)
    elif el.tag == 'UnaryOp':
        num = _num_str_from_unaryop_el(el)
    else:
        num = None
    return num

def num_str_from_parent_el(parent_el):
    child_els = parent_el.getchildren()
    if len(child_els) != 1:
        return None
    child_el = child_els[0]
    return num_str_from_el(child_el)
