from SpirentSLC.yaml_execution.matcher import YamlQuery, match
from SpirentSLC.yaml_execution.utils import compose, compose_all, dump, dump_all
from SpirentSLC.yaml_execution.matcher import MappingParentMatch, DocumentStreamMatch, SequenceParentMatch
from SpirentSLC.yaml_execution.errors import *
from yaml.nodes import MappingNode, SequenceNode, ScalarNode
from yaml.error import YAMLError


class YamlOperation:

    def __init__(self, query):
        self.query = query

    def compose_source(self, source):
        try:
            return list(compose_all(source))
        except YAMLError:
            raise InvalidSourceError('Failed to parse source YAML')


class YamlOperationWithValue(YamlOperation):
    def compose_value(self):
        try:
            return compose(self.value)
        except YAMLError:
            raise InvalidValueError('Failed to parse insertion value')

    def __init__(self, query, value):
        YamlOperation.__init__(self, query)
        self.value = value


class YamlGetOperation(YamlOperation):

    def __init__(self, query):
        YamlOperation.__init__(self, query)

    def execute(self, input):
        nodes = self.compose_source(input)
        matched_node = match(nodes, self.query)
        return dump(matched_node.value)


class YamlDeleteOperation(YamlOperation):

    def __init__(self, query):
        YamlOperation.__init__(self, query)

    def execute(self, input):
        nodes = self.compose_source(input)
        self.delete_node(match(nodes, self.query))
        return dump_all(nodes)

    def delete_node(self, match):
        if isinstance(match, DocumentStreamMatch):
            del match.documents[match.index]
        if isinstance(match, SequenceParentMatch):
            del match.sequence.value[match.index]
        if isinstance(match, MappingParentMatch):
            del match.mapping.value[match.index]


class YamlSetOperation(YamlOperationWithValue):

    def __init__(self, query, value):
        YamlOperationWithValue.__init__(self, query, value)

    def execute(self, input):
        nodes = self.compose_source(input)
        self.replace_node(match(nodes, self.query))
        return dump_all(nodes)

    def replace_node(self, match):
        new_node = self.compose_value()
        if isinstance(match, DocumentStreamMatch):
            match.documents[match.index] = new_node
        if isinstance(match, SequenceParentMatch):
            match.sequence.value[match.index] = new_node
        if isinstance(match, MappingParentMatch):
            match.mapping.value[match.index] = (match.entry[0], new_node)


class YamlAddOperation(YamlOperationWithValue):

    def __init__(self, query, value):
        YamlOperationWithValue.__init__(self, query, value)

    def compose_key(self):
        try:
            return compose(self.query.segments[-1])
        except YAMLError:
            raise InvalidQueryError('Failed to parse insertion key')

    def execute(self, input):
        nodes = self.compose_source(input)

        if len(self.query.segments) == 0:
            index = self.query.document_index
            if index < 0 or index > len(nodes):
                raise InvalidQueryError(
                    'Index path segment should be in range [{}, {}]'.format(0, len(nodes)))
            new_node = self.compose_value()
            nodes.insert(index, new_node)
        else:
            self.add_node(nodes)

        return dump_all(nodes)

    def add_node(self, nodes):
        # Match parent
        parent_query = YamlQuery(self.query.document_index, self.query.segments[:-1])
        parent_match = match(nodes, parent_query)
        container_node = parent_match.value

        if isinstance(container_node, MappingNode):
            key_segment = self.query.segments[-1]
            try:
                match([container_node], YamlQuery(0, [key_segment]))
                raise KeyExistsError('A mapping entry with the key \'{}\' already exists'.format(key_segment))
            except NotFoundError:
                new_key = self.compose_key()
                new_node = self.compose_value()
                container_node.value.append(tuple([new_key, new_node]))
                return

        if isinstance(container_node, SequenceNode):
            index_segment = self.query.segments[-1]
            try:
                index = int(index_segment)
            except ValueError:
                raise InvalidQueryError('Index path segment \'{}\' cannot be parsed to integer'.format(index_segment))
            if index < 0 or index > len(container_node.value):
                raise InvalidQueryError(
                    'Index path segment should be in range [{}, {}]'.format(0, len(self.query.segments)))
            new_node = self.compose_value()
            container_node.value.insert(index, new_node)
            return

        if isinstance(container_node, ScalarNode):
            raise InvalidQueryError('Can only add values into maps and sequences, but not scalars')

        raise ValueError('Unexpected type of node: {}'.format(type(container_node)))
