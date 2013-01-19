import sys
from xml.dom import minidom


def dappend(dictionary, key, item):
    if key in dictionary.keys():
        if not isinstance(dictionary[key], list):
            lst = []
            lst.append(dictionary[key])
            lst.append(item)
            dictionary[key] = lst
        else:
            dictionary[key].append(item)
    else:
        dictionary.setdefault(key, item)


def node_attributes(node):
    if node.hasAttributes():
        return dict([(str(attr),
            str(node.attributes[attr].value))
                for attr in node.attributes.keys()])
    else:
        return None


def attr_str(node):
    return "%s-attrs" % str(node.nodeName)


def hasAttributes(node):
    if node.nodeType == node.ELEMENT_NODE:
        if node.hasAttributes():
            return True
    return False


def with_attributes(node, values):
    if hasAttributes(node):
        if isinstance(values, dict):
            dappend(values, '#attributes', node_attributes(node))
            return {str(node.nodeName): values}
        elif isinstance(values, str):
            return {str(node.nodeName): values,
                attr_str(node): node_attributes(node)}
    else:
        return {str(node.nodeName): values}


def xmldom2dict(node):
    if not node.hasChildNodes():
        if node.nodeType == node.TEXT_NODE:
            if node.data.strip() != '':
                return str(node.data.strip())
            else:
                return None
        else:
            return with_attributes(node, None)
    else:
        childlist = [xmldom2dict(child)
            for child in node.childNodes
                if (xmldom2dict(child) != None
                    and child.nodeType != child.COMMENT_NODE)]
        if len(childlist) == 1:
            return with_attributes(node, childlist[0])
        else:
            new_dict = {}
            for child in childlist:
                if isinstance(child, dict):
                    for k in child:
                        dappend(new_dict, k, child[k])
                elif isinstance(child, str):
                    dappend(new_dict, '#text', child)
                else:
                    print "ERROR"
            return with_attributes(node, new_dict)


def lispy_string(node, lst=None, level=0):
    if lst == None:
        lst = []
    if not isinstance(node, dict) and not isinstance(node, list):
        lst.append(' "%s"' % node)
    elif isinstance(node, dict):
        for key in node.keys():
            lst.append("\n%s(%s" % (spaces(level), key))
            lispy_print(node[key], lst, level + 2)
            lst.append(")")
    elif isinstance(node, list):
        lst.append(" [")
        for item in node:
            lispy_print(item, lst, level)
        lst.append("]")
    return lst
