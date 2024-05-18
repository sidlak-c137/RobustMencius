from .utils import Message

class Request(Message):
    def __init__(self, args: dict = {}):
        super().__init__("Request", args)
        proto_args = set({
            "AMOCommand": "AMOCommand from client"
        })
        if not proto_args == set(args.keys()):
            raise ValueError("Request arguments must be: {}".format(proto_args))
        
class Response(Message):
    def __init__(self, args: dict = {}):
        super().__init__("Response", args)
        proto_args = set({
            "AMOCommand": "AMOCommand from client",
            "AMOResponse": "AMOResponse from server",
        })
        if not proto_args == set(args.keys()):
            raise ValueError("Response arguments must be: {}".format(proto_args))
