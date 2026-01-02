from http_client import HttpClient


class ResourceBase:
    """Base class for API resources"""
    def __init__(self, client: HttpClient):
        self._client = client