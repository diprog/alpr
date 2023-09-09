class HTTPError(Exception):
    def __init__(self, json, status: int):
        self.json = json
        self.status = status