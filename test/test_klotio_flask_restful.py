import unittest
import unittest.mock
import klotio_unittest

import os
import json
import yaml

import werkzeug.datastructures

import flask
import flask_restful

import klotio
import klotio_flask_restful


class TestRestful(klotio_unittest.TestCase):

    @classmethod
    @unittest.mock.patch("klotio.logger", klotio_unittest.MockLogger)
    def setUpClass(cls):

        cls.app = flask.Flask("klot-io-flask-restful")

        cls.app.logger = klotio.logger(cls.app.name)

        api = flask_restful.Api(cls.app)

        api.add_resource(klotio_flask_restful.Health, '/health')
        api.add_resource(Group, '/group')

        cls.api = cls.app.test_client()

    def setUp(self):

        self.app.logger.clear()

class TestFlask(TestRestful):

    def test_request_extra(self):

        request = unittest.mock.MagicMock()

        request.method = "madness"
        request.path = "forward"
        request.remote_addr = "here"
        request.args = werkzeug.datastructures.ImmutableMultiDict([('a', '1')])
        request.get_json.return_value = {"b": 2}

        self.assertEqual(klotio_flask_restful.request_extra(request), {
            "method": "madness",
            "path": "forward",
            "remote_addr": "here",
            "args": {"a": '1'},
            "json": {"b": 2}
        })

    def test_response_extra(self):

        self.assertEqual(klotio_flask_restful.response_extra({"a": 1}), {
            "status_code": 200,
            "json": {"a": 1}
        })

        self.assertEqual(klotio_flask_restful.response_extra([{"b": 2}, 201]), {
            "status_code": 201,
            "json": {"b": 2}
        })

    @unittest.mock.patch("traceback.format_exc")
    def test_logger(self, mock_traceback):

        @klotio_flask_restful.logger
        def good():
            return {"message": "yep"}, 202

        self.app.add_url_rule('/good', 'good', good)

        self.assertStatusValue(self.api.get("/good"), 202, "message", "yep")

        self.assertLogged(self.app.logger, "debug", "request", extra={
            "request": {
                "method": "GET",
                "path": "/good",
                "remote_addr": "127.0.0.1"
            }
        })

        self.assertStatusValue(self.api.get("/good?a=1", json={"b": 2}), 202, "message", "yep")

        self.assertLogged(self.app.logger, "debug", "request", extra={
            "request": {
                "method": "GET",
                "path": "/good",
                "remote_addr": "127.0.0.1",
                "args": {"a": '1'},
                "json": {"b": 2}
            }
        })

        self.assertLogged(self.app.logger, "debug", "response", extra={
            "response": {
                "status_code": 202,
                "json": {"message": "yep"}
            }
        })

        @klotio_flask_restful.logger
        def bad():
            raise Exception("whoops")

        mock_traceback.return_value = "logger"

        self.app.add_url_rule('/bad', 'bad', bad)

        response = self.api.get("/bad")
        self.assertStatusValue(response, 500, "message", "whoops")
        self.assertStatusValue(response, 500, "traceback", "logger")

        self.assertLogged(self.app.logger, "exception", "request failed")

        self.assertLogged(self.app.logger, "debug", "response", extra={
            "response": {
                "status_code": 500,
                "json": {
                    "message": "whoops",
                    "traceback": "logger"
                }
            }
        })

class TestHealth(TestRestful):

    def test_get(self):

        self.assertStatusValue(self.api.get("/health"), 200, "message", "OK")

        self.assertLogged(self.app.logger, "debug", "request", extra={
            "request": {
                "method": "GET",
                "path": "/health",
                "remote_addr": "127.0.0.1"
            }
        })

        self.assertLogged(self.app.logger, "debug", "response", extra={
            "response": {
                "status_code": 200,
                "json": {
                    "message": "OK"
                }
            }
        })

class Group(klotio_flask_restful.Group):
    APP = "unittest.klot.io"

class TestGroup(TestRestful):

    @unittest.mock.patch("requests.get")
    def test_get(self, mock_get):

        mock_get.return_value.json.return_value = [{
            "name": "unit",
            "url": "test"
        }]

        self.assertStatusValue(self.api.get("/group"), 200, "group", [{
            "name": "unit",
            "url": "test"
        }])

        mock_get.assert_has_calls([
            unittest.mock.call("http://api.klot-io/app/unittest.klot.io/member"),
            unittest.mock.call().raise_for_status(),
            unittest.mock.call().json()
        ])

        self.assertLogged(self.app.logger, "debug", "request", extra={
            "request": {
                "method": "GET",
                "path": "/group",
                "remote_addr": "127.0.0.1"
            }
        })

        self.assertLogged(self.app.logger, "debug", "response", extra={
            "response": {
                "status_code": 200,
                "json": {
                    "group": [{
                        "name": "unit",
                        "url": "test"
                    }]
                }
            }
        })
