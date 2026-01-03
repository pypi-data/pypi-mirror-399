import requests as _requests

DEFAULT_USER_AGENT = "Open-Sesame"


class Session(_requests.Session):
    def request(self, method, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = DEFAULT_USER_AGENT
        kwargs["headers"] = headers
        return super().request(method, url, **kwargs)


# Session افتراضية
_default_session = Session()


def request(method, url, **kwargs):
    return _default_session.request(method, url, **kwargs)

def get(url, **kwargs):
    return request("GET", url, **kwargs)

def post(url, **kwargs):
    return request("POST", url, **kwargs)

def put(url, **kwargs):
    return request("PUT", url, **kwargs)

def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)

def head(url, **kwargs):
    return request("HEAD", url, **kwargs)

def options(url, **kwargs):
    return request("OPTIONS", url, **kwargs)

def patch(url, **kwargs):
    return request("PATCH", url, **kwargs)


# تصدير باقي requests
exceptions = _requests.exceptions
codes = _requests.codes
utils = _requests.utils
cookies = _requests.cookies
compat = _requests.compat
status_codes = _requests.status_codes