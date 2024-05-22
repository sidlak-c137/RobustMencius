from .utils import Message


class Request(Message):
    def __init__(self, args: dict = {}):
        super().__init__("Request", args)
        proto_args = set({"AMOCommand": "AMOCommand from client"})
        if not proto_args == set(args.keys()):
            raise ValueError("Request arguments must be: {}".format(proto_args))


class Response(Message):
    def __init__(self, args: dict = {}):
        super().__init__("Response", args)
        proto_args = set(
            {
                "AMOCommand": "AMOCommand from client",
                "AMOResponse": "AMOResponse from server",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("Response arguments must be: {}".format(proto_args))


class ProposeRequest(Message):
    def __init__(self, args: dict = {}):
        super().__init__("ProposeRequest", args)
        proto_args = set(
            {
                "slot": "Slot of the log",
                "command": "AMOCommand from proposer",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("ProposeRequest arguments must be: {}".format(proto_args))

class ProposeReply(Message):
    def __init__(self, args: dict = {}):
        super().__init__("ProposeReply", args)
        proto_args = set(
            {
                "slot": "Slot of the log",
                "slot_out": "Slot out",
                "skip_till": "Slot to skip till",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("ProposeReply arguments must be: {}".format(proto_args))
        
class Heartbeat(Message):
    def __init__(self, args: dict = {}):
        super().__init__("Heartbeat", args)
        proto_args = set(
            {
                "log": "Log from acceptor",
                "slot_out": "Minimum slot out",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("Heartbeat arguments must be: {}".format(proto_args))

class HeartbeatReply(Message):
    def __init__(self, args: dict = {}):
        super().__init__("HeartbeatReply", args)
        proto_args = set(
            {
                "slot_out": "Slot out",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("HeartbeatReply arguments must be: {}".format(proto_args))