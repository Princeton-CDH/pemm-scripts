import pytest

from scripts import server

# see the flask docs for an explanation of creating an example test client:
# https://flask.palletsprojects.com/en/1.1.x/testing/#the-testing-skeleton

# see also the docs on mocking the 'g' context object:
# https://flask.palletsprojects.com/en/1.1.x/testing/#faking-resources

@pytest.fixture
def client():
    # FIXME incomplete
    server.app.config['TESTING'] = True

    with server.app.test_client() as client:
        with server.app.app_context():
            pass
        yield client

