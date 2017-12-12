"""
code adapted from:
https://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm/
"""
from typing import List

from .tuples import ExtensionTuple

PARENT_NODE = '__parent__'


class Node:
    def __init__(self, name, dependencies):
        self.name = name
        self.dependencies = dependencies
        self.dependent_nodes = []

    def add_dependent_node(self, node):
        self.dependent_nodes.append(node)

    def __repr__(self):
        return f'{self.name}: {self.dependencies!r}'


def _resolve_dependencies(node: Node, resolved: list, unresolved: list):
    unresolved.append(node)
    for dependent_node in node.dependent_nodes:
        if dependent_node not in resolved:
            if dependent_node in unresolved:
                raise Exception(
                    f'Circular dependency detected: {dependent_node.name} '
                    f'depends on an extension that depends on it.')
            _resolve_dependencies(dependent_node, resolved, unresolved)
    resolved.append(node)
    unresolved.remove(node)


def resolve_extension_order(extensions: List[ExtensionTuple]):
    nodes = {}
    for extension in extensions:
        nodes[extension.name] = Node(extension.name, extension.dependencies)

    parent_node = Node(PARENT_NODE, list(nodes.keys()))
    nodes[PARENT_NODE] = parent_node

    for name, node in nodes.items():
        for dependency_name in node.dependencies:
            node.add_dependent_node(nodes[dependency_name])

    order = []
    _resolve_dependencies(parent_node, order, [])
    return [node.name for node in order if node.name != PARENT_NODE]
