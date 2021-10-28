from lxml import etree  # @UnresolvedImport

def inspect_el(el):
    print(str(etree.tostring(el, pretty_print=True), encoding='utf-8'))
