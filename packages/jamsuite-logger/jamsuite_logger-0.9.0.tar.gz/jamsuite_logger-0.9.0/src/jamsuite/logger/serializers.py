import datetime
import json
import logging


def default_converter(obj):
    "converter used by json.dumps to format datetime"
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return str(obj)


class JSONSerializer(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.pretty_json = kwargs.pop("pretty", False)
        super().__init__(*args, **kwargs)

    def format(self, record) -> str:
        msg = super().format(record)
        # serialize msg as JSON
        return json.dumps(msg, default=default_converter)
