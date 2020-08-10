import requests
import functools
import traceback

import flask
import flask_restful


def request_extra(request):

    extra = {
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr
    }

    if hasattr(request, "args") and getattr(request, "args"):
        extra["args"] = getattr(request, "args").to_dict()

    if hasattr(request, "json") and getattr(request, "json"):
        extra["json"] = getattr(request, "json")

    return extra

def response_extra(response):

    extra = {}

    if isinstance(response, dict):
        return {
            "status_code": 200,
            "json": response
        }
    else:
        return {
            "status_code": response[1],
            "json": response[0]
        }

def require_logging(endpoint):

    @functools.wraps(endpoint)
    def wrap(*args, **kwargs):

        try:

            flask.current_app.logger.debug("request", extra={"request": request_extra(flask.request)})
            response = endpoint(*args, **kwargs)

        except Exception as exception:

            response = {
                "message": str(exception),
                "traceback": traceback.format_exc()
            }, 500

        flask.current_app.logger.debug("response", extra={"response": response_extra(response)})

        return response

    return wrap


class Health(flask_restful.Resource):

    @require_logging
    def get(self):
        return {"message": "OK"}


class Group(flask_restful.Resource):

    @require_logging
    def get(self):

        response = requests.get(f"http://api.klot-io/app/{self.APP}/member")

        response.raise_for_status()

        return {"group": response.json()}
