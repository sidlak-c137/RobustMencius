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


class PrepareRequest(Message):
    def __init__(self, args: dict = {}):
        super().__init__("PrepareRequest", args)
        proto_args = set(
            {
                "ballot": "Ballot from proposer",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("PrepareRequest arguments must be: {}".format(proto_args))


class PrepareReply(Message):
    def __init__(self, args: dict = {}):
        super().__init__("PrepareReply", args)
        proto_args = set(
            {
                "ballot": "Ballot from acceptor",
                "log": "Log from acceptor",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("PrepareReply arguments must be: {}".format(proto_args))


class ProposeRequest(Message):
    def __init__(self, args: dict = {}):
        super().__init__("ProposeRequest", args)
        proto_args = set(
            {
                "ballot": "Ballot from proposer",
                "slot": "slot",
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
                "ballot": "Ballot from acceptor",
                "slot": "slot",
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
                "ballot": "Ballot from proposer",
                "log": "Log from proposer",
                "min_slot_out": "Minimum slot out number",
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
                "ballot": "Ballot from acceptor",
                "slot_out": "Slot number",
                "sender": "Sender name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("HeartbeatReply arguments must be: {}".format(proto_args))
