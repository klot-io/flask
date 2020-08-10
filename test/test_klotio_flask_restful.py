import unittest
import unittest.mock
import klotio_unittest

import os
import json
import yaml

import werkzeug.datastructures

import flask
import flask_restful

import klotio_logger
import klotio_flask_restful


class TestRestful(klotio_unittest.TestCase):

    @classmethod
    @unittest.mock.patch("klotio_logger.setup", klotio_unittest.MockLogger)
    def setUpClass(cls):

        cls.app = flask.Flask("klot-io-flask-restful")

        cls.app.logger = klotio_logger.setup(cls.app.name)

        api = flask_restful.Api(cls.app)

        api.add_resource(klotio_flask_restful.Health, '/health')
        api.add_resource(Group, '/group')

        cls.api = cls.app.test_client()

    def test_request_extra(self):

        request = unittest.mock.MagicMock()

        request.method = "madness"
        request.path = "forward"
        request.remote_addr = "here"
        request.args = werkzeug.datastructures.ImmutableMultiDict([('a', '1')])
        request.json = {"b": 2}

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
    def test_require_logging(self, mock_traceback):

        @klotio_flask_restful.require_logging
        def good():
            return {"message": "yep"}, 202

        self.app.add_url_rule('/good', 'good', good)

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

        @klotio_flask_restful.require_logging
        def bad():
            raise Exception("whoops")

        mock_traceback.return_value = "adaisy"

        self.app.add_url_rule('/bad', 'bad', bad)

        response = self.api.get("/bad")
        self.assertStatusValue(response, 500, "message", "whoops")
        self.assertStatusValue(response, 500, "traceback", "adaisy")

        self.assertLogged(self.app.logger, "debug", "response", extra={
            "response": {
                "status_code": 500,
                "json": {
                    "message": "whoops",
                    "traceback": "adaisy"
                }
            }
        })

class TestHealth(TestRestful):

    def test_get(self):

        self.assertEqual(self.api.get("/health").json, {"message": "OK"})


class Group(klotio_flask_restful.Group):
    APP = "unittest.klot.io"

class TestGroup(TestRestful):

    @unittest.mock.patch("requests.get")
    def test_get(self, mock_get):

        mock_get.return_value.json.return_value = [{
            "name": "unit",
            "url": "test"
        }]

        self.assertEqual(self.api.get("/group").json, {"group": [{
            "name": "unit",
            "url": "test"
        }]})

        mock_get.assert_has_calls([
            unittest.mock.call("http://api.klot-io/app/unittest.klot.io/member"),
            unittest.mock.call().raise_for_status(),
            unittest.mock.call().json()
        ])
