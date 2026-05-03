from app.factory import create_app


def test_create_app_returns_app_instance():
    app = create_app("testing")
    assert app is not None
