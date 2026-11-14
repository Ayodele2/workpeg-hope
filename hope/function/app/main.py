"""The function half of this peg.

Workpeg calls ``main(context, payload)`` for each call: ``context`` says who
and what the call is about, and ``context["token"]`` is the one-call
credential to write back to the Tables API with; ``payload`` is the row's
data or the action's arguments. Try it offline with
``workpeg function test .`` in the peg's folder.
"""


def main(context, payload):
    return {"ok": True, "peg": "hope", "payload": payload}
