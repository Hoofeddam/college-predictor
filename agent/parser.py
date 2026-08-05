import json


def parse_response(response):

    try:
        return json.loads(response)

    except Exception:

        return {
            "type": "final",
            "answer": response
        }