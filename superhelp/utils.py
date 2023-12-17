from lxml import etree

def inspect_el(el):
    print(str(etree.tostring(el, pretty_print=True), encoding='utf-8'))
