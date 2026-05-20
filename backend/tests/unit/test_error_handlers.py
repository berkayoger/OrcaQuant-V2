def test_unhandled_exception_returns_generic_json_500(app):
    @app.route('/boom')
    def boom():
        raise RuntimeError('db-password=secret should never leak')

    client = app.test_client()
    res = client.get('/boom')
    assert res.status_code == 500
    assert res.get_json() == {"error": {"code": "internal_server_error", "message": "Internal server error"}}
