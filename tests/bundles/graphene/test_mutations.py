import pytest

from flask_unchained import unchained

from ._bundles.graphene_bundle.graphql import types

parent_manager = unchained.get_local_proxy('parent_manager')
child_manager = unchained.get_local_proxy('child_manager')


CREATE_PARENT = '''
  mutation createParent($name: String!, $children: [ID] = []) {
    createParent(name: $name, children: $children) {
      parent {
        id
        name
        children {
          id
        }
      }
    }
  }
'''

DELETE_PARENT = '''
  mutation deleteParent($id: ID!) {
    deleteParent(id: $id) {
      id
    }
  }
'''

EDIT_PARENT = '''
  mutation editParent($id: ID!, $name: String = "", $children: [ID] = []) {
    editParent(id: $id, name: $name, children: $children) {
      parent {
        id
        name
        children {
          id
        }
      }
    }
  }
'''


@pytest.mark.bundles(['flask_unchained.bundles.sqlalchemy',
                      'flask_unchained.bundles.graphene',
                      'tests.bundles.graphene._bundles.graphene_bundle'])
class TestParentMutations:
    def test_create_parent_requires_name(self, graphql_client):
        result = graphql_client.execute(CREATE_PARENT)

        assert 'errors' in result and len(result['errors']) == 1
        assert result['errors'][0]['message'] == \
               'Variable "$name" of required type "String!" was not provided.'

    def test_create_parent_works_without_children(self, graphql_client):
        result = graphql_client.execute(CREATE_PARENT, dict(name='parent'))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'createParent' in result['data']
        assert 'parent' in result['data']['createParent']

        result = result['data']['createParent']['parent']
        parent = parent_manager.get(id=result['id'])

        assert dict(result) == dict(id=str(parent.id),
                                    name=parent.name,
                                    children=parent.children)

    def test_create_parent_works_with_children(self, graphql_client):
        children = child_manager.all()[:2]
        result = graphql_client.execute(CREATE_PARENT, dict(
            name='parent',
            children=[child.id for child in children],
        ))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'createParent' in result['data']
        assert 'parent' in result['data']['createParent']

        result = result['data']['createParent']['parent']
        parent = parent_manager.get(id=result['id'])

        assert dict(result) == dict(id=str(parent.id),
                                    name=parent.name,
                                    children=[{'id': str(child.id)}
                                              for child in children])

    def test_delete_parent_requires_id(self, graphql_client):
        result = graphql_client.execute(DELETE_PARENT)

        assert 'errors' in result and len(result['errors']) == 1
        assert result['errors'][0]['message'] == \
               'Variable "$id" of required type "ID!" was not provided.'

    def test_delete_parent_works_with_id(self, graphql_client):
        parent = parent_manager.get_by(name='parent_one')
        child_ids = [child.id for child in parent.children]

        result = graphql_client.execute(DELETE_PARENT, dict(id=parent.id))
        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'deleteParent' in result['data']
        assert parent_manager.get(result['data']['deleteParent']['id']) is None

        # deletion of parent should cascade delete children
        for child_id in child_ids:
            assert child_manager.get(child_id) is None

    def test_edit_parent_requires_id(self, graphql_client):
        result = graphql_client.execute(EDIT_PARENT)

        assert 'errors' in result and len(result['errors']) == 1
        assert result['errors'][0]['message'] == \
               'Variable "$id" of required type "ID!" was not provided.'

    def test_edit_parent_name(self, graphql_client):
        parent = parent_manager.get_by(name='parent_one')
        result = graphql_client.execute(EDIT_PARENT, dict(id=parent.id,
                                                          name='new-name'))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'editParent' in result['data'] and 'parent' in result['data']['editParent']

        result = result['data']['editParent']['parent']
        assert dict(result) == dict(id=str(parent.id),
                                    name='new-name',
                                    children=[{'id': str(child.id)}
                                              for child in parent.children])

    def test_edit_parent_children(self, graphql_client):
        parent = parent_manager.get_by(name='parent_one')
        children = child_manager.filter(~child_manager.Meta.model.id.in_(
            child.id for child in parent.children))
        result = graphql_client.execute(EDIT_PARENT, dict(id=parent.id,
                                                          children=[child.id for child
                                                                    in children]))

        assert 'errors' not in result and 'data' in result, result['errors']
        assert 'editParent' in result['data'] and 'parent' in result['data']['editParent']

        result = result['data']['editParent']['parent']
        assert dict(result) == dict(id=str(parent.id),
                                    name=parent.name,
                                    children=[{'id': str(child.id)}
                                              for child in children])
