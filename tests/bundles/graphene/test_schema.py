import pytest

from flask_unchained import unchained


parent_manager = unchained.get_local_proxy('parent_manager')
child_manager = unchained.get_local_proxy('child_manager')


GET_CHILD = '''
query Child($id: ID!) {
  child(id: $id) {
    id
    name
    parent {
      id
      name
    }
  }
}
'''

GET_CHILDREN = '''
{
  children {
    id
    name
    parent {
      id
      name
    }
  }
}
'''

GET_PARENT = '''
query Parent($id: ID!) {
  parent(id: $id) {
    id
    name
    children {
      id
      name
    }
  }
}
'''

GET_PARENTS = '''
{
  parents {
    id
    name
    children {
      id
      name
    }
  }
}
'''


@pytest.mark.bundles(['flask_unchained.bundles.sqlalchemy',
                      'flask_unchained.bundles.graphene',
                      'tests.bundles.graphene._bundles.graphene_bundle'])
class TestSchema:
    def test_get_child(self, graphql_client):
        child = child_manager.get_by(name='child_one')
        result = graphql_client.execute(GET_CHILD, dict(id=child.id))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'child' in result['data']

        assert dict(result['data']['child']) == dict(
            id=str(child.id),
            name=child.name,
            parent=dict(id=str(child.parent.id), name=child.parent.name))

    def test_get_children(self, graphql_client):
        result = graphql_client.execute(GET_CHILDREN)

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'children' in result['data']

        results = result['data']['children']
        children = child_manager.all()
        assert results and len(results) == len(children)

        for result, child in zip(results, children):
            assert dict(result) == dict(
                id=str(child.id),
                name=child.name,
                parent=dict(id=str(child.parent.id), name=child.parent.name))

    def test_get_parent(self, graphql_client):
        parent = parent_manager.get_by(name='parent_one')
        result = graphql_client.execute(GET_PARENT, dict(id=str(parent.id)))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'parent' in result['data']

        assert dict(result['data']['parent']) == dict(
            id=str(parent.id),
            name=parent.name,
            children=[{'id': str(child.id), 'name': child.name}
                      for child in parent.children])

    def test_get_parents(self, graphql_client, parents):
        result = graphql_client.execute(GET_PARENTS)

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'parents' in result['data']

        results = result['data']['parents']
        assert results and len(results) == len(parents)

        for result, parent in zip(results, parents):
            assert dict(result) == dict(
                id=str(parent.id),
                name=parent.name,
                children=[{'id': str(child.id), 'name': child.name}
                          for child in parent.children])
