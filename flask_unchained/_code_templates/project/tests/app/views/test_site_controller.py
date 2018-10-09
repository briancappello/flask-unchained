def test_get_index(client):
    r = client.get('site_controller.index')
    assert r.status_code == 200
