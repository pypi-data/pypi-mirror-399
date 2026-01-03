from collections import deque
from yaml.nodes import MappingNode, SequenceNode, ScalarNode
from yaml.error import YAMLError
from SpirentSLC.yaml_execution.utils import compose, equals
from SpirentSLC.yaml_execution.errors import InvalidQueryError, NotFoundError


class YamlQuery:

    def __init__(self, document_index, segments):
        self.document_index = document_index
        self.segments = segments


class Match:
    def __init__(self, value):
        self.value = value


class DocumentStreamMatch(Match):
    def __init__(self, document, documents, index):
        Match.__init__(self, document)
        self.document = document
        self.documents = documents
        self.index = index


class MappingParentMatch(Match):
    def __init__(self, mapping, entry, index):
        Match.__init__(self, entry[1])
        self.mapping = mapping
        self.entry = entry
        self.index = index


class SequenceParentMatch(Match):
    def __init__(self, sequence, item, index):
        Match.__init__(self, item)
        self.sequence = sequence
        self.item = item
        self.index = index


def match(nodes, query):
    index = query.document_index
    if index < 0 or index >= len(nodes):
        raise NotFoundError('No document found of index {}'.format(index))
    document = nodes[index]
    segments = deque(query.segments)

    if len(segments) == 0:
        return DocumentStreamMatch(document, nodes, index)

    return match_node(document, segments)


def match_node(node, segments):
    segment = segments.popleft()
    if isinstance(node, MappingNode):
        for i, entry in zip(range(len(node.value)), node.value):
            if key_matches(entry[0], segment):
                match_index = i
                break
        else:
            raise NotFoundError('No matches found in mapping node for key \'{}\''.format(segment))

        if len(segments) == 0:
            return MappingParentMatch(node, node.value[match_index], match_index)

        return match_node(node.value[match_index][1], segments)

    if isinstance(node, SequenceNode):
        try:
            match_index = int(segment)
        except ValueError:
            raise InvalidQueryError('Index query segment \'{}\' cannot be parsed to integer'.format(segment))
        if match_index < 0 or match_index >= len(node.value):
            raise NotFoundError('No matches found in sequence node for index {}'.format(match_index))

        if len(segments) == 0:
            return SequenceParentMatch(node, node.value[match_index], match_index)

        return match_node(node.value[match_index], segments)

    if isinstance(node, ScalarNode):
        raise InvalidQueryError('Cannot iterate over scalar nodes')

    raise ValueError('Unexpected type of node: {}'.format(type(node)))


def key_matches(key_node, segment):
    try:
        segment_node = compose(segment)
        return equals(key_node, segment_node)
    except YAMLError as e:
        raise InvalidQueryError('Unexpected syntax in query segment: {}'.format(e.message))
