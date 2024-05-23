from .utils import Timer


class RequestTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("RequestTimer", 200, args)
        proto_args = set(
            {
                "message": "request message",
                "name": "server name",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("RequestTimer arguments must be: {}".format(proto_args))


class HeartbeatTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("HeartbeatTimer", 50, args)
        proto_args = set(
            {
                "ballot": "ballot",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("HeartbeatTimer arguments must be: {}".format(proto_args))


class HeartbeatCheckTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("HeartbeatCheckTimer", 200, args)
        proto_args = set({})
        if not proto_args == set(args.keys()):
            raise ValueError(
                "HeartbeatCheckTimer arguments must be: {}".format(proto_args)
            )


class PrepareTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("PrepareTimer", 100, args)
        proto_args = set(
            {
                "ballot": "ballot",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("PrepareTimer arguments must be: {}".format(proto_args))


class ProposeTimer(Timer):
    def __init__(self, args: dict = {}):
        super().__init__("ProposeTimer", 100, args)
        proto_args = set(
            {
                "ballot": "ballot",
            }
        )
        if not proto_args == set(args.keys()):
            raise ValueError("ProposeTimer arguments must be: {}".format(proto_args))
