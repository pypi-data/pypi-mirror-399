import itertools

import yaml
from yaml.dumper import Emitter, Serializer, Representer, Resolver
from yaml.loader import Reader, Scanner, Composer, Constructor, Resolver
from yaml.emitter import DocumentStartEvent, StreamEndEvent, EmitterError
from yaml.parser import Parser
from yaml.nodes import Node, MappingNode, SequenceNode, ScalarNode


class DummyRepresenter(Representer):
    def __init__(self):
        Representer.__init__(self)

    def represent_data(self, data):
        return data


class ImplicitEndEmitter(Emitter):
    def __init__(self, stream, canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None):
        Emitter.__init__(self, stream, canonical=canonical,
                         indent=indent, width=width,
                         allow_unicode=allow_unicode, line_break=line_break)

    def expect_document_start(self, first=False):
        if isinstance(self.event, DocumentStartEvent):
            Emitter.expect_document_start(self, first=first)
        elif isinstance(self.event, StreamEndEvent):
            self.write_stream_end()
            self.state = self.expect_nothing
        else:
            raise EmitterError("expected DocumentStartEvent or StreamEndEvent, but got %s"
                               % self.event)


class AnchorSerializer(Serializer):
    def __init__(self, encoding=None,
                 explicit_start=True, explicit_end=False, version=None, tags=None):
        Serializer.__init__(self, encoding=encoding,
                            explicit_start=explicit_start, explicit_end=False,
                            version=version, tags=tags)

    def generate_anchor(self, node):
        return node.anchor


class AnchorComposer(Composer):
    def __init__(self):
        Composer.__init__(self)

    def compose_scalar_node(self, anchor):
        node = Composer.compose_scalar_node(self, anchor)
        node.anchor = anchor
        return node

    def compose_mapping_node(self, anchor):
        node = Composer.compose_mapping_node(self, anchor)
        node.anchor = anchor
        return node

    def compose_sequence_node(self, anchor):
        node = Composer.compose_sequence_node(self, anchor)
        node.anchor = anchor
        return node


class NamedAnchorsLoader(Reader, Scanner, Parser, AnchorComposer, Constructor, Resolver):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        AnchorComposer.__init__(self)
        Constructor.__init__(self)
        Resolver.__init__(self)


class NodeDumper(ImplicitEndEmitter, AnchorSerializer, DummyRepresenter, Resolver):

    def __init__(self, stream, default_style=None, default_flow_style=None,
                 canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None,
                 encoding=None, explicit_start=None, explicit_end=None,
                 version=None, tags=None, sort_keys=True):
        ImplicitEndEmitter.__init__(self, stream, canonical=canonical,
                                    indent=indent, width=width,
                                    allow_unicode=allow_unicode, line_break=line_break)
        AnchorSerializer.__init__(self, encoding=encoding,
                                  explicit_start=explicit_start, explicit_end=False,
                                  version=version, tags=tags)
        DummyRepresenter.__init__(self)
        Resolver.__init__(self)


def compose_all(input):
    documents_iterable = yaml.compose_all(stream=input, Loader=NamedAnchorsLoader)
    try:
        first = next(documents_iterable)
    except StopIteration:
        return yaml.compose_all('""', Loader=NamedAnchorsLoader)
    return itertools.chain([first], documents_iterable)


def dump_all(nodes):
    return yaml.dump_all(nodes, explicit_start=True, Dumper=NodeDumper)


def compose(input):
    result = yaml.compose(stream=input, Loader=NamedAnchorsLoader)
    return result if result is not None else yaml.compose('""', Loader=NamedAnchorsLoader)


def dump(nodes):
    return yaml.dump(nodes, explicit_start=False, Dumper=NodeDumper)


def equals(node1, node2):
    if type(node1) != type(node2):
        return False

    if node1.tag != node2.tag:
        return False

    if isinstance(node1, MappingNode):
        return mapping_equals(node1, node2)
    if isinstance(node1, SequenceNode):
        return sequence_equals(node1, node2)
    if isinstance(node1, ScalarNode):
        return scalar_equals(node1, node2)
    raise ValueError('Expected node of type MappingNode, SequenceNode or ScalarNode, but got {}'.format(type(node1)))


def scalar_equals(node1, node2):
    return node1.value == node2.value


def mapping_equals(node1, node2):
    if len(node1.value) != len(node2.value):
        return False

    map1 = dict(node1.value)
    map2 = dict(node2.value)

    shared_keys = []

    for key1 in map1.keys():
        for key2 in map2.keys():
            if equals(key1, key2):
                shared_keys.append(tuple([key1, key2]))
                break

    if len(shared_keys) != len(map1):
        return False

    for key1, key2 in shared_keys:
        if not equals(map1[key1], map2[key2]):
            return False

    return True


def sequence_equals(node1, node2):
    if len(node1.value) != len(node2.value):
        return False

    for item1, item2 in zip(node1.value, node2.value):
        if not equals(item1, item2):
            return False

    return True
