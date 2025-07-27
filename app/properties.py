import json


class Properties:
    def __init__(self, file="properties.json"):
        with open(file) as file:
            data = json.load(file)

            self.port = data['port']


