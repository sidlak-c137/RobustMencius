from .utils import Timer

class RequestTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("RequestTimer", 200, args)
        proto_args = set({
            "message": "request message",
            "name": "server name",
        })
        if not proto_args == set(args.keys()):
            raise ValueError("RequestTimer arguments must be: {}".format(proto_args))